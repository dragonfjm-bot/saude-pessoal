from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UrinaryRecord(Base):
    __tablename__ = "urinary_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    quantity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    color: Mapped[str | None] = mapped_column(String(40), nullable=True)
    odor_intensity: Mapped[str | None] = mapped_column(String(20), nullable=True)
    symptoms: Mapped[str | None] = mapped_column(String(200), nullable=True)
    water_ml: Mapped[int | None] = mapped_column(Integer, nullable=True)
    observations: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
