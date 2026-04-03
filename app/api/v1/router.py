"""
API router.

Main router that aggregates all endpoint routers.
Follows the Composition pattern.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import users

api_router = APIRouter()

api_router.include_router(users.router, prefix="/users", tags=["Users"])
