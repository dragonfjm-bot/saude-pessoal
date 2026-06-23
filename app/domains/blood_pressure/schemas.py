from datetime import datetime

from pydantic import BaseModel, Field, field_validator


BP_CONTEXTS = [
    ("repouso", "Repouso"),
    ("manha", "Manhã"),
    ("tarde", "Tarde"),
    ("noite", "Noite"),
    ("apos_esforco", "Após esforço"),
    ("apos_medicacao", "Após medicação"),
    ("stress", "Stress"),
    ("outro", "Outro"),
]


class BloodPressureForm(BaseModel):
    measured_at: datetime
    systolic: int = Field(ge=60, le=300)
    diastolic: int = Field(ge=40, le=200)
    heart_rate: int | None = Field(default=None, ge=30, le=250)
    context: str | None = None
    observations: str | None = None

    @field_validator("heart_rate", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v

    @field_validator("context", "observations", mode="before")
    @classmethod
    def empty_str_none(cls, v):
        return v if v else None
