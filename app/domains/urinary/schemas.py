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

WATER_AMOUNTS = [
    (125, "125 ml"),
    (250, "250 ml"),
    (375, "375 ml"),
    (500, "500 ml"),
    (625, "625 ml"),
    (750, "750 ml"),
    (875, "875 ml"),
    (1000, "1,0 L"),
    (1250, "1,25 L"),
    (1500, "1,5 L"),
    (1750, "1,75 L"),
    (2000, "2,0 L"),
    (2500, "2,5 L"),
    (3000, "3,0 L"),
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
    water_ml: int | None = None
    observations: str | None = None

    @field_validator("quantity", "color", "odor_intensity", "observations", mode="before")
    @classmethod
    def empty_str_none(cls, v):
        return v if v else None

    @field_validator("water_ml", mode="before")
    @classmethod
    def parse_water(cls, v):
        if not v:
            return None
        return int(v)
