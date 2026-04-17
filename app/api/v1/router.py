# app/api/v1/router.py

from fastapi import APIRouter

from app.api.v1.endpoints import health, pdf

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(pdf.router, prefix="/pdf", tags=["PDF"])