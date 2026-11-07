from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class WorkStatus(str, Enum):
    QUEUED = "QUEUED"
    EM_DIAGNOSTICO = "EM_DIAGNOSTICO"
    EM_EXECUCAO = "EM_EXECUCAO"
    DONE = "DONE"


@dataclass
class WorkOrder:
    os_id: int
    status: WorkStatus = WorkStatus.QUEUED
    id: int | None = None
    correlation_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def start_diagnosis(self) -> None:
        if self.status != WorkStatus.QUEUED:
            raise ValueError("work order não está na fila")
        self.status = WorkStatus.EM_DIAGNOSTICO
        self.updated_at = datetime.now(UTC)

    def finish_diagnosis(self) -> None:
        if self.status != WorkStatus.EM_DIAGNOSTICO:
            raise ValueError("diagnóstico não iniciado")
        self.status = WorkStatus.QUEUED
        self.updated_at = datetime.now(UTC)

    def start_execution(self) -> None:
        self.status = WorkStatus.EM_EXECUCAO
        self.updated_at = datetime.now(UTC)

    def complete(self) -> None:
        self.status = WorkStatus.DONE
        self.updated_at = datetime.now(UTC)
