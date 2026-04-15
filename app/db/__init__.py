"""
Database module.

Manages database connections and sessions.
Follows the Dependency Inversion Principle.
"""

from app.db.database import MongoDatabase, SessionManager
from app.db.migrations.manager import MigrationManager

__all__ = ["MongoDatabase", "SessionManager", "MigrationManager"]
