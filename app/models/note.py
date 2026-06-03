from datetime import datetime

from app.core.database import Base

from sqlalchemy import Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Note(Base):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    job_application_id: Mapped[int] = mapped_column(
        ForeignKey("job_applications.id"),
        nullable=False
    )

    content: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    job_application = relationship(
        "JobApplication",
        back_populates="notes"
    )