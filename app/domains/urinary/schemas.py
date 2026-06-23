from datetime import datetime

from pydantic import BaseModel, field_validator


QUANTITIES = [("pouca", "Pouca"), ("normal", "Normal"), ("muita", "Muita")]

COLORS = [
    ("clara", "Clara"),
    ("amarela_clara", "Amarela clara"),
    ("amarela", "Amarela"),
    ("amarela_escura", "Amarela escura"),
    ("ambar", "Âmbar"),
    ("turva", "Turva"),
    ("rosada", "Rosada"),
    ("outra", "Outra"),
]

ODORS = [
    ("sem_odor", "Sem odor"),
    ("suave", "Suave"),
    ("moderado", "Moderado"),
    ("intenso", "Intenso"),
]

SYMPTOMS = [
    ("ardor", "Ardor"),
    ("dor", "Dor"),
    ("urgencia", "Urgência"),
    ("desconforto", "Desconforto"),
    ("frequencia_aumentada", "Frequência aumentada"),
    ("dificuldade", "Dificuldade em urinar"),
]


class UrinaryForm(BaseModel):
    recorded_at: datetime
    quantity: str | None = None
    color: str | None = None
    odor_intensity: str | None = None
    symptoms: str | None = None
    observations: str | None = None

    @field_validator("quantity", "color", "odor_intensity", "observations", mode="before")
    @classmethod
    def empty_str_none(cls, v):
        return v if v else None
