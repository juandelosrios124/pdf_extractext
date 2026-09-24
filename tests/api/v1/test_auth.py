import os
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.exceptions import UnauthorizedException

os.environ["DEBUG"] = "true"

from app.api.v1.endpoints.auth import get_current_user
from app.main import create_application
from app.schemas.auth import Token
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service
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


class TestAuthEndpoint:
    def test_login_returns_token(self, client):
        token = Token(access_token="header.payload.signature")

        with patch.object(auth_service, "login", AsyncMock(return_value=token)) as mock_login:
            response = client.post(
                "/api/v1/auth/login",
                json={"identifier": "testuser", "password": "plain-password"},
            )

        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"
        mock_login.assert_awaited_once()

    def test_login_returns_401_for_invalid_credentials(self, client):
        with patch.object(
            auth_service,
            "login",
            AsyncMock(
                side_effect=UnauthorizedException("Incorrect username/email or password")
            ),
        ):
            response = client.post(
                "/api/v1/auth/login",
                json={"identifier": "testuser", "password": "wrong-password"},
            )

        assert response.status_code == 401
        assert response.json()["detail"] == "Incorrect username/email or password"

    def test_me_returns_current_user(self, client):
        app = client.app
        app.dependency_overrides[get_current_user] = lambda: UserResponse(
            id="507f1f77bcf86cd799439011",
            email="user@example.com",
            username="testuser",
            full_name="Test User",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )

        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer header.payload.signature"},
        )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        assert response.json()["username"] == "testuser"
