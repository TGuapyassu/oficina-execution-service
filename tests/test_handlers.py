import json

from app.application.handlers import handle_event
from app.infrastructure.db import get_by_os, get_session_factory, init_db
from oficina_contracts.events import DomainEvent
from oficina_contracts.routing import RoutingKey


def test_handle_os_created():
    init_db()
    session = get_session_factory()()
    ev = DomainEvent.create(RoutingKey.OS_CREATED, os_id=99, correlation_id="c1")
    handle_event(session, ev.model_dump_json().encode())
    session.commit()
    wo = get_by_os(session, 99)
    assert wo is not None
    assert wo.status.value == "EM_DIAGNOSTICO"
    session.close()
