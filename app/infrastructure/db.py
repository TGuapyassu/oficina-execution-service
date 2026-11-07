from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.domain.work_order import WorkOrder, WorkStatus
from app.settings import get_settings


class Base(DeclarativeBase):
    pass


class WorkOrderOrm(Base):
    __tablename__ = "work_orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    os_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    status: Mapped[str] = mapped_column(String(32))
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


_engine = None
_Session: sessionmaker[Session] | None = None


def get_engine():
    global _engine
    if _engine is None:
        url = get_settings().database_url
        kw = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
        _engine = create_engine(url, pool_pre_ping=True, future=True, **kw)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _Session
    if _Session is None:
        _Session = sessionmaker(get_engine(), expire_on_commit=False)
    return _Session


def init_db() -> None:
    Base.metadata.create_all(get_engine())


def save_work(session: Session, wo: WorkOrder) -> WorkOrder:
    if wo.id is None:
        row = WorkOrderOrm(
            os_id=wo.os_id,
            status=wo.status.value,
            correlation_id=wo.correlation_id,
            created_at=wo.created_at,
            updated_at=wo.updated_at,
        )
        session.add(row)
        session.flush()
        wo.id = row.id
    else:
        row = session.get(WorkOrderOrm, wo.id)
        assert row is not None
        row.status = wo.status.value
        row.updated_at = wo.updated_at
    return wo


def get_by_os(session: Session, os_id: int) -> WorkOrder | None:
    row = session.execute(select(WorkOrderOrm).where(WorkOrderOrm.os_id == os_id)).scalar_one_or_none()
    if row is None:
        return None
    return WorkOrder(
        id=row.id,
        os_id=row.os_id,
        status=WorkStatus(row.status),
        correlation_id=row.correlation_id,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )
