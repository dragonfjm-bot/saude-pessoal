import csv
import io
import json
from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.urinary.models import UrinaryRecord
from app.domains.urinary.schemas import UrinaryForm


class UrinaryService:
    def __init__(self, db: Session):
        self.db = db

    # ── CRUD ──────────────────────────────────────────────────────────────

    def create(self, form: UrinaryForm) -> UrinaryRecord:
        record = UrinaryRecord(**form.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record_id: int, form: UrinaryForm) -> UrinaryRecord | None:
        record = self.db.get(UrinaryRecord, record_id)
        if not record:
            return None
        for k, v in form.model_dump().items():
            setattr(record, k, v)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record_id: int) -> bool:
        record = self.db.get(UrinaryRecord, record_id)
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True

    def get_by_id(self, record_id: int) -> UrinaryRecord | None:
        return self.db.get(UrinaryRecord, record_id)

    def list(
        self,
        page: int = 1,
        per_page: int = 20,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[UrinaryRecord], int]:
        q = select(UrinaryRecord)
        if date_from:
            q = q.where(UrinaryRecord.recorded_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            q = q.where(UrinaryRecord.recorded_at <= datetime.combine(date_to, datetime.max.time()))
        q = q.order_by(UrinaryRecord.recorded_at.desc())

        total = self.db.scalar(select(func.count()).select_from(q.subquery()))
        records = list(self.db.scalars(q.offset((page - 1) * per_page).limit(per_page)))
        return records, total or 0

    # ── Aggregates ────────────────────────────────────────────────────────

    def get_today_count(self) -> int:
        today = date.today()
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
        return self.db.scalar(
            select(func.count(UrinaryRecord.id)).where(
                UrinaryRecord.recorded_at.between(start, end)
            )
        ) or 0

    def get_chart_data(self, period: str = "month") -> dict:
        days_map = {"week": 7, "month": 30, "3months": 90}
        since = datetime.now() - timedelta(days=days_map.get(period, 30))
        records = list(
            self.db.scalars(
                select(UrinaryRecord)
                .where(UrinaryRecord.recorded_at >= since)
                .order_by(UrinaryRecord.recorded_at)
            )
        )

        counts: dict[str, int] = defaultdict(int)
        for r in records:
            key = r.recorded_at.strftime("%d/%m")
            counts[key] += 1

        labels = sorted(counts.keys(), key=lambda d: datetime.strptime(d, "%d/%m"))
        return {"labels": labels, "counts": [counts[l] for l in labels]}

    # ── Export ────────────────────────────────────────────────────────────

    def export_csv(self) -> str:
        records, _ = self.list(per_page=100_000)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Data/Hora", "Quantidade", "Cor", "Odor", "Sintomas", "Água (ml)", "Observações"])
        for r in records:
            writer.writerow([
                r.id, r.recorded_at.strftime("%Y-%m-%d %H:%M"),
                r.quantity or "", r.color or "", r.odor_intensity or "",
                r.symptoms or "", r.water_ml if r.water_ml is not None else "", r.observations or "",
            ])
        return output.getvalue()

    def export_json(self) -> str:
        records, _ = self.list(per_page=100_000)
        data = [
            {
                "id": r.id,
                "recorded_at": r.recorded_at.isoformat(),
                "quantity": r.quantity,
                "color": r.color,
                "odor_intensity": r.odor_intensity,
                "symptoms": r.symptoms,
                "water_ml": r.water_ml,
                "observations": r.observations,
            }
            for r in records
        ]
        return json.dumps(data, ensure_ascii=False, indent=2)
