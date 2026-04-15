"""
Migration Manager.

Manages execution and tracking of MongoDB migrations.
"""

import importlib
import inspect
import logging
import pkgutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Type

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.migrations.base import (
    Migration,
    MigrationError,
    MigrationRecord,
    MigrationStatus,
)

logger = logging.getLogger(__name__)

MIGRATIONS_COLLECTION = "_migrations"


class MigrationManager:
    """
    Manages MongoDB migrations.

    Responsibilities:
    1. Discover and register migrations
    2. Track migration history
    3. Execute pending migrations
    4. Support rollback operations
    5. Ensure migration idempotency

    Usage:
        manager = MigrationManager()
        await manager.initialize()
        await manager.run_migrations()
    """

    def __init__(self, migrations_package: str = "app.db.migrations.scripts"):
        """
        Initialize migration manager.

        Args:
            migrations_package: Package path containing migration scripts.
        """
        self.migrations_package = migrations_package
        self._migrations: Dict[str, Type[Migration]] = {}
        self._db: Optional[AsyncIOMotorDatabase] = None

    async def initialize(self, db: AsyncIOMotorDatabase) -> None:
        """
        Initialize migration manager with database.

        Args:
            db: MongoDB database instance.
        """
        self._db = db
        await self._ensure_migrations_collection()
        await self._discover_migrations()

    async def _ensure_migrations_collection(self) -> None:
        """Ensure migrations collection exists with proper indexes."""
        if self._db is None:
            raise MigrationError("Database not initialized")

        # Check if collection exists
        collections = await self._db.list_collection_names()
        if MIGRATIONS_COLLECTION not in collections:
            logger.info(f"Creating migrations collection: {MIGRATIONS_COLLECTION}")

        # Create index on migration_id for fast lookups
        await self._db[MIGRATIONS_COLLECTION].create_index(
            "migration_id", unique=True, background=True
        )

    async def _discover_migrations(self) -> None:
        """Discover all migration classes in the migrations package."""
        try:
            package = importlib.import_module(self.migrations_package)
            package_path = Path(package.__file__).parent

            for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
                full_module_name = f"{self.migrations_package}.{module_name}"
                try:
                    module = importlib.import_module(full_module_name)

                    # Find Migration subclasses
                    for name, obj in inspect.getmembers(module):
                        if (
                            inspect.isclass(obj)
                            and issubclass(obj, Migration)
                            and obj is not Migration
                            and hasattr(obj, "migration_id")
                            and obj.migration_id
                        ):
                            self._migrations[obj.migration_id] = obj
                            logger.debug(
                                f"Discovered migration: {obj.migration_id} - {obj.name}"
                            )

                except Exception as e:
                    logger.error(
                        f"Error loading migration module {full_module_name}: {e}"
                    )

            logger.info(f"Discovered {len(self._migrations)} migrations")

        except ImportError:
            logger.warning(f"Migrations package not found: {self.migrations_package}")

    async def get_migration_history(self) -> List[MigrationRecord]:
        """
        Get migration execution history.

        Returns:
            List of migration records ordered by execution time.
        """
        if self._db is None:
            raise MigrationError("Database not initialized")

        cursor = self._db[MIGRATIONS_COLLECTION].find().sort("started_at", 1)
        records = await cursor.to_list(length=1000)
        return [MigrationRecord.from_dict(r) for r in records]

    async def get_pending_migrations(self) -> List[Type[Migration]]:
        """
        Get migrations that haven't been executed yet.

        Returns:
            List of pending migration classes sorted by ID.
        """
        if self._db is None:
            raise MigrationError("Database not initialized")

        # Get executed migration IDs
        executed = await self._db[MIGRATIONS_COLLECTION].distinct("migration_id")

        # Filter pending migrations
        pending = [
            migration_class
            for migration_id, migration_class in self._migrations.items()
            if migration_id not in executed
        ]

        # Sort by migration ID (chronological order)
        return sorted(pending, key=lambda m: m.migration_id)

    async def run_migrations(
        self, target: Optional[str] = None
    ) -> List[MigrationRecord]:
        """
        Run pending migrations.

        Args:
            target: Optional target migration ID to migrate up/down to.

        Returns:
            List of executed migration records.
        """
        if self._db is None:
            raise MigrationError("Database not initialized")

        pending = await self.get_pending_migrations()
        executed = []

        if target:
            # Filter migrations up to target
            pending = [m for m in pending if m.migration_id <= target]

        if not pending:
            logger.info("No pending migrations")
            return []

        logger.info(f"Running {len(pending)} migrations")

        for migration_class in pending:
            record = await self._run_migration(migration_class)
            executed.append(record)

            if record.status == MigrationStatus.FAILED:
                logger.error(f"Migration failed: {record.migration_id}")
                break

        return executed

    async def _run_migration(self, migration_class: Type[Migration]) -> MigrationRecord:
        """
        Execute a single migration.

        Args:
            migration_class: Migration class to execute.

        Returns:
            Migration record with execution results.
        """
        if self._db is None:
            raise MigrationError("Database not initialized")

        migration = migration_class()
        migration.validate()

        record = MigrationRecord(
            migration_id=migration.migration_id,
            name=migration.name,
            description=migration.description,
            status=MigrationStatus.RUNNING,
            started_at=datetime.utcnow(),
        )

        logger.info(f"Running migration: {record.migration_id} - {record.name}")

        try:
            # Save running status
            await self._db[MIGRATIONS_COLLECTION].insert_one(record.to_dict())

            # Execute pre-upgrade hook
            await migration.pre_upgrade(self._db)

            # Execute migration
            await migration.upgrade(self._db)

            # Execute post-upgrade hook
            await migration.post_upgrade(self._db)

            # Mark as successful
            record.status = MigrationStatus.SUCCESS
            record.completed_at = datetime.utcnow()
            record.execution_time_ms = int(
                (record.completed_at - record.started_at).total_seconds() * 1000
            )

            logger.info(f"Migration completed: {record.migration_id}")

        except Exception as e:
            record.status = MigrationStatus.FAILED
            record.completed_at = datetime.utcnow()
            record.error_message = str(e)
            logger.error(f"Migration failed: {record.migration_id} - {e}")

        # Update record
        await self._db[MIGRATIONS_COLLECTION].update_one(
            {"migration_id": record.migration_id},
            {"$set": record.to_dict()},
        )

        return record

    async def rollback_migration(self, migration_id: str) -> MigrationRecord:
        """
        Rollback a specific migration.

        Args:
            migration_id: ID of migration to rollback.

        Returns:
            Updated migration record.
        """
        if self._db is None:
            raise MigrationError("Database not initialized")

        if migration_id not in self._migrations:
            raise MigrationError(f"Migration not found: {migration_id}")

        migration_class = self._migrations[migration_id]
        migration = migration_class()

        # Get existing record
        doc = await self._db[MIGRATIONS_COLLECTION].find_one(
            {"migration_id": migration_id}
        )
        if not doc or MigrationStatus(doc["status"]) != MigrationStatus.SUCCESS:
            raise MigrationError(
                f"Migration not executed or not successful: {migration_id}"
            )

        record = MigrationRecord.from_dict(doc)
        record.status = MigrationStatus.RUNNING

        try:
            await migration.downgrade(self._db)
            record.status = MigrationStatus.ROLLED_BACK
            record.completed_at = datetime.utcnow()
            logger.info(f"Migration rolled back: {migration_id}")
        except Exception as e:
            record.status = MigrationStatus.FAILED
            record.error_message = str(e)
            logger.error(f"Migration rollback failed: {migration_id} - {e}")
            raise

        await self._db[MIGRATIONS_COLLECTION].update_one(
            {"migration_id": migration_id},
            {"$set": record.to_dict()},
        )

        return record

    async def get_status(self) -> Dict[str, Any]:
        """
        Get migration system status.

        Returns:
            Dictionary with migration status information.
        """
        pending = await self.get_pending_migrations()
        history = await self.get_migration_history()

        return {
            "total_migrations": len(self._migrations),
            "pending_count": len(pending),
            "executed_count": len(history),
            "pending_ids": [m.migration_id for m in pending],
            "last_executed": history[-1].migration_id if history else None,
        }


# Singleton instance
migration_manager = MigrationManager()
