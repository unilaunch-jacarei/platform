import os

import pytest

from backend.config import get_settings


@pytest.fixture(autouse=True, scope="session")
def setup_test_environment():
    """Sets default testing environment variables for all test sessions."""
    os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
    os.environ["JWT_SECRET"] = "test-jwt-secret-key-minimum-32-chars-long!"
    os.environ["ENVIRONMENT"] = "testing"
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
