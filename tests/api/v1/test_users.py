import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import ConflictException

os.environ["DEBUG"] = "true"

from app.main import create_application
from app.schemas.user import UserResponse
from app.services.user_service import user_service
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.fixture
def client():
    with patch("app.main.db.connect", AsyncMock()), \
         patch("app.main.db.disconnect", AsyncMock()), \
         patch("app.main.db.get_database", MagicMock(return_value=MagicMock())), \
         patch("app.main.MigrationRunner") as mock_runner_cls:

        mock_runner_cls.return_value.migrate = AsyncMock()

        app = create_application()

        with TestClient(app) as test_client:
            yield test_client


class TestUsersEndpoint:
    def test_create_user_returns_201(self, client):
        response_model = UserResponse(
            id="507f1f77bcf86cd799439011",
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        with patch.object(
            user_service, "create_user", AsyncMock(return_value=response_model)
        ) as mock_create_user:
            response = client.post(
                "/api/v1/users/",
                json={
                    "email": "user@example.com",
                    "username": "testuser",
                    "full_name": "Test User",
                    "password": "plain-password",
                },
            )

        assert response.status_code == 201
        data = response.json()
        assert data["id"] == "507f1f77bcf86cd799439011"
        assert data["email"] == "user@example.com"
        mock_create_user.assert_awaited_once()

    def test_create_user_returns_409_for_conflict(self, client):
        with patch.object(
            user_service,
            "create_user",
            AsyncMock(side_effect=ConflictException("Email already registered")),
        ):
            response = client.post(
                "/api/v1/users/",
                json={
                    "email": "user@example.com",
                    "username": "testuser",
                    "full_name": "Test User",
                    "password": "plain-password",
                },
            )

        assert response.status_code == 409
        assert response.json()["detail"] == "Email already registered"
