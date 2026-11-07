import pytest
from fastapi.testclient import TestClient

from app.application.handlers import handle_event
from app.domain.work_order import WorkStatus
from app.infrastructure.db import get_by_os, get_session_factory
from app.main import app
from oficina_contracts.events import DomainEvent
from oficina_contracts.routing import RoutingKey


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def _seed_os_created(os_id: int) -> None:
    session = get_session_factory()()
    ev = DomainEvent.create(RoutingKey.OS_CREATED, os_id=os_id, correlation_id="c-test")
    handle_event(session, ev.model_dump_json().encode())
    session.commit()
    session.close()


def test_health_and_ready(client: TestClient):
    assert client.get("/health").json()["status"] == "ok"
    body = client.get("/ready").json()
    assert body["status"] == "ok"


def test_get_work_order_404(client: TestClient):
    assert client.get("/work-orders/404").status_code == 404


def test_get_work_order_after_event(client: TestClient):
    _seed_os_created(10)
    r = client.get("/work-orders/10")
    assert r.status_code == 200
    assert r.json()["status"] == WorkStatus.EM_DIAGNOSTICO.value


def test_queue_snapshot(client: TestClient):
    """Sem Redis local, `/queue` responde lista vazia — smoke do endpoint."""
    r = client.get("/queue")
    assert r.status_code == 200
    assert "items" in r.json()


def test_advance_diagnosis(client: TestClient):
    _seed_os_created(12)
    r = client.post("/work-orders/12/advance-diagnosis")
    assert r.status_code == 200
    session = get_session_factory()()
    wo = get_by_os(session, 12)
    assert wo is not None
    assert wo.status == WorkStatus.EM_DIAGNOSTICO
    session.close()
