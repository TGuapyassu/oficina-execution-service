from __future__ import annotations

import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from app.domain.work_order import WorkStatus
from app.infrastructure.db import get_by_os, get_session_factory, init_db
from app.infrastructure.messaging import start_consumer
from app.infrastructure.redis_queue import ExecutionQueue
from app.settings import get_settings

_stop: threading.Event | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _stop
    init_db()
    _stop = threading.Event()
    start_consumer(_stop)
    yield
    if _stop:
        _stop.set()


app = FastAPI(title="Oficina Execution Service", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    return {
        "status": "ok",
        "redis": ExecutionQueue().ping(),
        "rabbitmq_configured": bool(get_settings().rabbitmq_url),
    }


@app.get("/work-orders/{os_id}")
def get_work_order(os_id: int) -> dict:
    session = get_session_factory()()
    try:
        wo = get_by_os(session, os_id)
        if wo is None:
            raise HTTPException(404, "Work order não encontrada")
        return {"os_id": wo.os_id, "status": wo.status.value, "id": wo.id}
    finally:
        session.close()


@app.get("/queue")
def queue_snapshot() -> dict:
    return {"items": ExecutionQueue().peek()}


@app.post("/work-orders/{os_id}/advance-diagnosis")
def advance_diagnosis(os_id: int) -> dict:
    """Uso operacional / testes: força conclusão de diagnóstico."""
    session = get_session_factory()()
    try:
        wo = get_by_os(session, os_id)
        if wo is None:
            raise HTTPException(404, "Work order não encontrada")
        if wo.status != WorkStatus.EM_DIAGNOSTICO:
            raise HTTPException(409, "Status inválido para diagnóstico")
        from app.infrastructure.publisher import publish
        from oficina_contracts.events import DomainEvent
        from oficina_contracts.routing import RoutingKey

        publish(
            RoutingKey.EXECUTION_DIAGNOSIS_COMPLETED.value,
            DomainEvent.create(RoutingKey.EXECUTION_DIAGNOSIS_COMPLETED, os_id=os_id).model_dump(mode="json"),
        )
        session.commit()
        return {"ok": True}
    finally:
        session.close()
