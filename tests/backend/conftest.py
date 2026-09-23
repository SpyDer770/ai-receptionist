import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import database
from main import app


@pytest.fixture()
def client():
    """
    Gives each test a fresh, isolated database and a TestClient
    connected to the real FastAPI app.
    """
    tmp_dir = tempfile.TemporaryDirectory()
    tmp_path = Path(tmp_dir.name) / "test_receptionist.db"

    database.set_db_path(tmp_path)
    database.init_db()

    with TestClient(app) as test_client:
        yield test_client

    database.set_db_path(database.DB_PATH)
    tmp_dir.cleanup()