
import pytest
from app import create_app


@pytest.fixture
def app(tmp_path):
    database_file = tmp_path / "test_hotel.db"

    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret",
        "DATABASE": str(database_file)
    })

    yield application


@pytest.fixture
def client(app):
    return app.test_client()
