import json

from app.application.handlers import handle_event
from app.infrastructure.db import get_by_os, get_session_factory, init_db
from oficina_contracts.events import DomainEvent
from oficina_contracts.routing import RoutingKey


def test_handle_payment_confirmed():
    init_db()
    session = get_session_factory()()
    ev = DomainEvent.create(RoutingKey.PAYMENT_CONFIRMED, os_id=50, correlation_id="c2")
    handle_event(session, ev.model_dump_json().encode())
    session.commit()
    wo = get_by_os(session, 50)
    assert wo is not None
    assert wo.status.value == "DONE"
    session.close()
