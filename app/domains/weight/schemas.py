from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class WeightForm(BaseModel):
    measured_at: datetime
    weight_kg: float = Field(gt=20, lt=500)
    observations: str | None = None

    @field_validator("observations", mode="before")
    @classmethod
    def empty_str_none(cls, v):
        return v if v else None
