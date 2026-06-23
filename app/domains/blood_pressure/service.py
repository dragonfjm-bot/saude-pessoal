import csv
import io
import json
from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domains.blood_pressure.models import BloodPressure
from app.domains.blood_pressure.schemas import BloodPressureForm


class BloodPressureService:
    def __init__(self, db: Session):
        self.db = db

    # ── CRUD ──────────────────────────────────────────────────────────────

    def create(self, form: BloodPressureForm) -> BloodPressure:
        record = BloodPressure(**form.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def update(self, record_id: int, form: BloodPressureForm) -> BloodPressure | None:
        record = self.db.get(BloodPressure, record_id)
        if not record:
            return None
        for k, v in form.model_dump().items():
            setattr(record, k, v)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, record_id: int) -> bool:
        record = self.db.get(BloodPressure, record_id)
        if not record:
            return False
        self.db.delete(record)
        self.db.commit()
        return True

    def get_by_id(self, record_id: int) -> BloodPressure | None:
        return self.db.get(BloodPressure, record_id)

    def list(
        self,
        page: int = 1,
        per_page: int = 20,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[BloodPressure], int]:
        q = select(BloodPressure)
        if date_from:
            q = q.where(BloodPressure.measured_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            q = q.where(BloodPressure.measured_at <= datetime.combine(date_to, datetime.max.time()))
        q = q.order_by(BloodPressure.measured_at.desc())

        total = self.db.scalar(select(func.count()).select_from(q.subquery()))
        records = list(self.db.scalars(q.offset((page - 1) * per_page).limit(per_page)))
        return records, total or 0

    # ── Aggregates ────────────────────────────────────────────────────────

    def get_latest(self) -> BloodPressure | None:
        return self.db.scalar(
            select(BloodPressure).order_by(BloodPressure.measured_at.desc()).limit(1)
        )

    def get_week_stats(self) -> dict:
        since = datetime.now() - timedelta(days=7)
        records = list(
            self.db.scalars(select(BloodPressure).where(BloodPressure.measured_at >= since))
        )
        if not records:
            return {}
        hr_values = [r.heart_rate for r in records if r.heart_rate]
        return {
            "avg_systolic": round(sum(r.systolic for r in records) / len(records), 1),
            "avg_diastolic": round(sum(r.diastolic for r in records) / len(records), 1),
            "avg_heart_rate": round(sum(hr_values) / len(hr_values), 1) if hr_values else None,
            "count": len(records),
        }

    def get_chart_data(self, period: str = "month") -> dict:
        days_map = {"week": 7, "month": 30, "3months": 90, "year": 365}
        since = datetime.now() - timedelta(days=days_map.get(period, 30))
        records = list(
            self.db.scalars(
                select(BloodPressure)
                .where(BloodPressure.measured_at >= since)
                .order_by(BloodPressure.measured_at)
            )
        )

        groups: dict[str, list[BloodPressure]] = defaultdict(list)
        for r in records:
            if period in ("week", "month"):
                key = r.measured_at.strftime("%d/%m")
            elif period == "3months":
                key = f"S{r.measured_at.strftime('%W/%y')}"
            else:
                key = r.measured_at.strftime("%b/%y")
            groups[key].append(r)

        labels, sys_data, dia_data, hr_data = [], [], [], []
        for label in list(dict.fromkeys(
            r.measured_at.strftime("%d/%m" if period in ("week", "month") else
                                   f"S{r.measured_at.strftime('%W/%y')}" if period == "3months" else "%b/%y")
            for r in records
        )):
            recs = groups[label]
            labels.append(label)
            sys_data.append(round(sum(r.systolic for r in recs) / len(recs), 1))
            dia_data.append(round(sum(r.diastolic for r in recs) / len(recs), 1))
            hr_vals = [r.heart_rate for r in recs if r.heart_rate]
            hr_data.append(round(sum(hr_vals) / len(hr_vals), 1) if hr_vals else None)

        return {"labels": labels, "systolic": sys_data, "diastolic": dia_data, "heart_rate": hr_data}

    # ── Classification ────────────────────────────────────────────────────

    @staticmethod
    def classify(systolic: int, diastolic: int) -> dict:
        if systolic > 180 or diastolic > 120:
            return {"css": "badge-crisis", "label": "Crise Hipertensiva"}
        if systolic >= 140 or diastolic >= 90:
            return {"css": "badge-danger", "label": "Hipertensão Grau 2"}
        if systolic >= 130 or diastolic >= 80:
            return {"css": "badge-warning", "label": "Hipertensão Grau 1"}
        if systolic >= 120:
            return {"css": "badge-elevated", "label": "Elevada"}
        return {"css": "badge-success", "label": "Normal"}

    # ── Export ────────────────────────────────────────────────────────────

    def export_csv(self) -> str:
        records, _ = self.list(per_page=100_000)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Data/Hora", "Sistólica", "Diastólica", "FC (bpm)", "Contexto", "Observações"])
        for r in records:
            writer.writerow([
                r.id, r.measured_at.strftime("%Y-%m-%d %H:%M"),
                r.systolic, r.diastolic, r.heart_rate or "",
                r.context or "", r.observations or "",
            ])
        return output.getvalue()

    def export_json(self) -> str:
        records, _ = self.list(per_page=100_000)
        data = [
            {
                "id": r.id,
                "measured_at": r.measured_at.isoformat(),
                "systolic": r.systolic,
                "diastolic": r.diastolic,
                "heart_rate": r.heart_rate,
                "context": r.context,
                "observations": r.observations,
            }
            for r in records
        ]
        return json.dumps(data, ensure_ascii=False, indent=2)
