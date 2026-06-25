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
    (125, "125 ml — copo pequeno"),
    (200, "200 ml — copo normal"),
    (330, "330 ml — lata"),
    (500, "500 ml — garrafa pequena"),
    (750, "750 ml — garrafa média"),
    (1000, "1000 ml — garrafa 1 L"),
    (1500, "1500 ml — garrafa 1,5 L"),
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
