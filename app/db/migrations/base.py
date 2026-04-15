"""
Base migration classes.

Defines the structure for MongoDB migrations.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class MigrationStatus(Enum):
    """Migration execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationRecord:
    """
    Record of a migration execution.

    Stored in MongoDB to track migration history.
    """

    migration_id: str
    name: str
    description: str
    status: MigrationStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MongoDB storage."""
        return {
            "_id": self.migration_id,
            "migration_id": self.migration_id,
            "name": self.name,
            "description": self.description,
            "status": self.status.value,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "execution_time_ms": self.execution_time_ms,
            "error_message": self.error_message,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MigrationRecord":
        """Create from MongoDB document."""
        return cls(
            migration_id=data["migration_id"],
            name=data["name"],
            description=data.get("description", ""),
            status=MigrationStatus(data["status"]),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            execution_time_ms=data.get("execution_time_ms"),
            error_message=data.get("error_message"),
            metadata=data.get("metadata", {}),
        )


class Migration(ABC):
    """
    Abstract base class for migrations.

    Each migration should:
    1. Have a unique ID (timestamp-based recommended: YYYYMMDDHHMMSS)
    2. Implement `upgrade` for forward migration
    3. Optionally implement `downgrade` for rollback

    Example:
        class AddUserIndexesMigration(Migration):
            migration_id = "20240115120000"
            name = "add_user_indexes"
            description = "Add indexes to users collection"

            async def upgrade(self, db):
                await db["users"].create_index("email", unique=True)
                await db["users"].create_index("username", unique=True)

            async def downgrade(self, db):
                await db["users"].drop_index("email_1")
                await db["users"].drop_index("username_1")
    """

    # Must be overridden in subclasses
    migration_id: str = ""
    name: str = ""
    description: str = ""

    @abstractmethod
    async def upgrade(self, db) -> None:
        """
        Execute migration.

        Args:
            db: MongoDB database instance.

        Raises:
            MigrationError: If migration fails.
        """
        pass

    async def downgrade(self, db) -> None:
        """
        Rollback migration.

        Args:
            db: MongoDB database instance.

        Raises:
            MigrationError: If rollback fails.

        Note:
            Override if rollback is supported.
            Default implementation raises NotImplementedError.
        """
        raise NotImplementedError(
            f"Rollback not implemented for migration {self.migration_id}"
        )

    async def pre_upgrade(self, db) -> None:
        """
        Hook executed before upgrade.

        Args:
            db: MongoDB database instance.
        """
        pass

    async def post_upgrade(self, db) -> None:
        """
        Hook executed after successful upgrade.

        Args:
            db: MongoDB database instance.
        """
        pass

    def validate(self) -> bool:
        """
        Validate migration configuration.

        Returns:
            True if valid, False otherwise.
        """
        if not self.migration_id:
            raise ValueError("Migration ID is required")
        if not self.name:
            raise ValueError("Migration name is required")
        return True


class MigrationError(Exception):
    """Exception raised for migration errors."""

    def __init__(self, message: str, migration_id: Optional[str] = None):
        self.message = message
        self.migration_id = migration_id
        super().__init__(self.message)


class SchemaVersion:
    """
    Tracks schema version for documents.

    Used for schema evolution - documents can be migrated
    on-the-fly when read.
    """

    CURRENT_VERSION = 1

    @classmethod
    def add_version(cls, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add schema version to document.

        Args:
            document: Document to version.

        Returns:
            Document with version field.
        """
        if "_schema_version" not in document:
            document["_schema_version"] = cls.CURRENT_VERSION
        return document

    @classmethod
    def migrate_document(
        cls, document: Dict[str, Any], target_version: int = CURRENT_VERSION
    ) -> Dict[str, Any]:
        """
        Migrate document to target schema version.

        Args:
            document: Document to migrate.
            target_version: Target schema version.

        Returns:
            Migrated document.
        """
        current_version = document.get("_schema_version", 0)

        while current_version < target_version:
            current_version = cls._migrate_up(document, current_version)

        document["_schema_version"] = target_version
        return document

    @classmethod
    def _migrate_up(cls, document: Dict[str, Any], from_version: int) -> int:
        """
        Migrate document up one version.

        Override this method to add migration logic
        for each version increment.

        Args:
            document: Document to migrate.
            from_version: Current version.

        Returns:
            New version number.
        """
        if from_version == 0:
            # Example: Add default fields
            document.setdefault("created_at", datetime.utcnow())
            document.setdefault("updated_at", datetime.utcnow())
            return 1

        # Add more version migrations here
        return from_version + 1
