import csv
import io
import json
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.weight.models import WeightRecord
from app.domains.weight.schemas import WeightForm


class WeightService:
    def __init__(self, db: Session):
        self.db = db

    # ── CRUD ──────────────────────────────────────────────────────────────

    def create(self, form: WeightForm) -> WeightRecord:
        record = WeightRecord(**form.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record_id: int, form: WeightForm) -> WeightRecord | None:
        record = self.db.get(WeightRecord, record_id)
        if not record:
            return None
        for k, v in form.model_dump().items():
            setattr(record, k, v)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record_id: int) -> bool:
        record = self.db.get(WeightRecord, record_id)
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True

    def get_by_id(self, record_id: int) -> WeightRecord | None:
        return self.db.get(WeightRecord, record_id)

    def list(
        self,
        page: int = 1,
        per_page: int = 20,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[WeightRecord], int]:
        q = select(WeightRecord)
        if date_from:
            q = q.where(WeightRecord.measured_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            q = q.where(WeightRecord.measured_at <= datetime.combine(date_to, datetime.max.time()))
        q = q.order_by(WeightRecord.measured_at.desc())

        total = self.db.scalar(select(func.count()).select_from(q.subquery()))
        records = list(self.db.scalars(q.offset((page - 1) * per_page).limit(per_page)))
        return records, total or 0

    # ── Aggregates ────────────────────────────────────────────────────────

    def get_latest(self) -> WeightRecord | None:
        return self.db.scalar(
            select(WeightRecord).order_by(WeightRecord.measured_at.desc()).limit(1)
        )

    def get_trend(self) -> dict:
        records = list(
            self.db.scalars(
                select(WeightRecord)
                .order_by(WeightRecord.measured_at.desc())
                .limit(2)
            )
        )
        if len(records) < 2:
            return {"direction": "neutral", "diff": 0.0}
        diff = round(records[0].weight_kg - records[1].weight_kg, 2)
        return {
            "direction": "up" if diff > 0 else "down" if diff < 0 else "neutral",
            "diff": abs(diff),
        }

    def get_chart_data(self, period: str = "month") -> dict:
        days_map = {"month": 30, "3months": 90, "6months": 180, "year": 365}
        since = datetime.now() - timedelta(days=days_map.get(period, 30))
        records = list(
            self.db.scalars(
                select(WeightRecord)
                .where(WeightRecord.measured_at >= since)
                .order_by(WeightRecord.measured_at)
            )
        )
        labels = [r.measured_at.strftime("%d/%m") for r in records]
        weights = [r.weight_kg for r in records]
        return {"labels": labels, "weights": weights}

    # ── Export ────────────────────────────────────────────────────────────

    def export_csv(self) -> str:
        records, _ = self.list(per_page=100_000)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Data/Hora", "Peso (kg)", "Observações"])
        for r in records:
            writer.writerow([
                r.id, r.measured_at.strftime("%Y-%m-%d %H:%M"),
                r.weight_kg, r.observations or "",
            ])
        return output.getvalue()

    def export_json(self) -> str:
        records, _ = self.list(per_page=100_000)
        data = [
            {
                "id": r.id,
                "measured_at": r.measured_at.isoformat(),
                "weight_kg": r.weight_kg,
                "observations": r.observations,
            }
            for r in records
        ]
        return json.dumps(data, ensure_ascii=False, indent=2)
