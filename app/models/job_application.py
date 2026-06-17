from datetime import datetime, timezone
from decimal import Decimal

from app.core.database import Base

from sqlalchemy import Integer, String, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )
    
    company: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False
    )

    position: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(255),
        default="applied",
        nullable=False
    )

    salary: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    link: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=None,
        nullable=True
    )

    notes = relationship(
        "Note",
        back_populates="job_application"
    )

    user = relationship(
        "User",
        back_populates="job_applications"
    )