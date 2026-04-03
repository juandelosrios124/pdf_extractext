"""
API tests for user endpoints.

Tests HTTP endpoints and response formats.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """Test user creation endpoint."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "apitest@example.com",
            "username": "apitestuser",
            "password": "securepassword123",
            "full_name": "API Test User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "apitest@example.com"
    assert data["username"] == "apitestuser"
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient):
    """Test user listing endpoint."""
    response = await client.get("/api/v1/users/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    """Test getting non-existent user."""
    response = await client.get("/api/v1/users/99999")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
