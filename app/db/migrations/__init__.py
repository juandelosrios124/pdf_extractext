"""
MongoDB Migration System.

Custom migration system for MongoDB since Alembic is designed for SQL databases.
This system provides versioned data transformations and schema evolution.

Why not Alembic?
----------------
1. Alembic is tightly coupled to SQLAlchemy (SQL ORM)
2. MongoDB is schemaless - no DDL needed
3. Schema changes are handled at application level
4. Migrations focus on data transformations, not schema
"""

from app.db.migrations.manager import MigrationManager
from app.db.migrations.base import Migration, MigrationStatus

__all__ = ["MigrationManager", "Migration", "MigrationStatus"]
