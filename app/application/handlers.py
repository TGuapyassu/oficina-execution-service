from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.domain.work_order import WorkOrder
from app.infrastructure.db import get_by_os, save_work
from app.infrastructure.messaging import publish
from app.infrastructure.redis_queue import ExecutionQueue
from oficina_contracts.events import DomainEvent
from oficina_contracts.routing import RoutingKey


def handle_event(session: Session, body: bytes) -> None:
    data = json.loads(body)
    key = data.get("routing_key", "")
    os_id = data.get("os_id")
    if os_id is None:
        return
    correlation_id = data.get("correlation_id")
    queue = ExecutionQueue()
    if key == RoutingKey.OS_CREATED.value:
        existing = get_by_os(session, os_id)
        if existing:
            return
        wo = WorkOrder(os_id=os_id, correlation_id=correlation_id)
        wo.start_diagnosis()
        save_work(session, wo)
        queue.enqueue(os_id, correlation_id)
        publish(
            RoutingKey.EXECUTION_QUEUED.value,
            DomainEvent.create(RoutingKey.EXECUTION_QUEUED, os_id=os_id, correlation_id=correlation_id).model_dump(mode="json"),
        )
        publish(
            RoutingKey.EXECUTION_STATUS_CHANGED.value,
            DomainEvent.create(
                RoutingKey.EXECUTION_STATUS_CHANGED,
                os_id=os_id,
                correlation_id=correlation_id,
                status="EM_DIAGNOSTICO",
            ).model_dump(mode="json"),
        )
        publish(
            RoutingKey.EXECUTION_DIAGNOSIS_COMPLETED.value,
            DomainEvent.create(
                RoutingKey.EXECUTION_DIAGNOSIS_COMPLETED,
                os_id=os_id,
                correlation_id=correlation_id,
            ).model_dump(mode="json"),
        )
    elif key == RoutingKey.PAYMENT_CONFIRMED.value:
        wo = get_by_os(session, os_id)
        if wo is None:
            wo = WorkOrder(os_id=os_id, correlation_id=correlation_id)
            save_work(session, wo)
        wo.start_execution()
        save_work(session, wo)
        publish(
            RoutingKey.EXECUTION_STARTED.value,
            DomainEvent.create(RoutingKey.EXECUTION_STARTED, os_id=os_id, correlation_id=correlation_id).model_dump(mode="json"),
        )
        publish(
            RoutingKey.EXECUTION_STATUS_CHANGED.value,
            DomainEvent.create(
                RoutingKey.EXECUTION_STATUS_CHANGED,
                os_id=os_id,
                correlation_id=correlation_id,
                status="EM_EXECUCAO",
            ).model_dump(mode="json"),
        )
        wo.complete()
        save_work(session, wo)
        publish(
            RoutingKey.EXECUTION_COMPLETED.value,
            DomainEvent.create(RoutingKey.EXECUTION_COMPLETED, os_id=os_id, correlation_id=correlation_id).model_dump(mode="json"),
        )
