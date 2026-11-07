from fastapi.testclient import TestClient

from app.infrastructure.db import init_db
from app.main import app

init_db()
client = TestClient(app)


def test_health():
    assert client.get("/health").status_code == 200
