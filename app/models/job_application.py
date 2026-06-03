from datetime import datetime
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
        default="Applied",
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
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    notes = relationship(
        "Note",
        back_populates="job_application"
    )

    user = relationship(
        "User",
        back_populates="job_applications"
    )