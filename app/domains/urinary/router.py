from datetime import date, datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import ITEMS_PER_PAGE, TEMPLATES_DIR
from app.database import get_session
from app.domains.urinary.schemas import COLORS, ODORS, QUANTITIES, SYMPTOMS, WATER_AMOUNTS, UrinaryForm
from app.domains.urinary.service import UrinaryService

router = APIRouter(prefix="/urologia", tags=["urinary"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def _svc(db: Session = Depends(get_session)) -> UrinaryService:
    return UrinaryService(db)


@router.get("", response_class=HTMLResponse)
def uri_list(
    request: Request,
    page: int = 1,
    date_from: date | None = None,
    date_to: date | None = None,
    svc: UrinaryService = Depends(_svc),
):
    records, total = svc.list(page=page, per_page=ITEMS_PER_PAGE, date_from=date_from, date_to=date_to)
    total_pages = max(1, -(-total // ITEMS_PER_PAGE))
    water_deltas = {r.id: svc.get_water_delta(r) for r in records}
    return templates.TemplateResponse(
        "urinary/list.html",
        {
            "request": request,
            "active_page": "urinary",
            "records": records,
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "date_from": date_from,
            "date_to": date_to,
            "water_deltas": water_deltas,
            "msg": request.query_params.get("msg"),
        },
    )


@router.get("/novo", response_class=HTMLResponse)
def uri_new(request: Request):
    return templates.TemplateResponse(
        "urinary/form.html",
        {
            "request": request,
            "active_page": "urinary",
            "record": None,
            "quantities": QUANTITIES,
            "colors": COLORS,
            "odors": ODORS,
            "symptoms_options": SYMPTOMS,
            "water_amounts": WATER_AMOUNTS,
            "now": datetime.now().strftime("%Y-%m-%dT%H:%M"),
            "errors": [],
        },
    )


@router.post("/novo")
def uri_create(
    request: Request,
    recorded_at: str = Form(...),
    quantity: str = Form(""),
    color: str = Form(""),
    odor_intensity: str = Form(""),
    symptoms: list[str] = Form(default=[]),
    water_ml: str = Form(""),
    observations: str = Form(""),
    svc: UrinaryService = Depends(_svc),
):
    try:
        form = UrinaryForm(
            recorded_at=datetime.fromisoformat(recorded_at),
            quantity=quantity or None,
            color=color or None,
            odor_intensity=odor_intensity or None,
            symptoms=",".join(symptoms) if symptoms else None,
            water_ml=water_ml or None,
            observations=observations or None,
        )
        svc.create(form)
        return RedirectResponse("/urologia?msg=Registo+criado+com+sucesso", status_code=303)
    except Exception as exc:
        return templates.TemplateResponse(
            "urinary/form.html",
            {
                "request": request,
                "active_page": "urinary",
                "record": None,
                "quantities": QUANTITIES,
                "colors": COLORS,
                "odors": ODORS,
                "symptoms_options": SYMPTOMS,
                "water_amounts": WATER_AMOUNTS,
                "now": recorded_at,
                "errors": [str(exc)],
            },
            status_code=422,
        )


@router.get("/{record_id}/editar", response_class=HTMLResponse)
def uri_edit(record_id: int, request: Request, svc: UrinaryService = Depends(_svc)):
    record = svc.get_by_id(record_id)
    if not record:
        return RedirectResponse("/urologia")
    return templates.TemplateResponse(
        "urinary/form.html",
        {
            "request": request,
            "active_page": "urinary",
            "record": record,
            "quantities": QUANTITIES,
            "colors": COLORS,
            "odors": ODORS,
            "symptoms_options": SYMPTOMS,
            "water_amounts": WATER_AMOUNTS,
            "now": record.recorded_at.strftime("%Y-%m-%dT%H:%M"),
            "selected_symptoms": record.symptoms.split(",") if record.symptoms else [],
            "errors": [],
        },
    )


@router.post("/{record_id}/editar")
def uri_update(
    record_id: int,
    request: Request,
    recorded_at: str = Form(...),
    quantity: str = Form(""),
    color: str = Form(""),
    odor_intensity: str = Form(""),
    symptoms: list[str] = Form(default=[]),
    water_ml: str = Form(""),
    observations: str = Form(""),
    svc: UrinaryService = Depends(_svc),
):
    try:
        form = UrinaryForm(
            recorded_at=datetime.fromisoformat(recorded_at),
            quantity=quantity or None,
            color=color or None,
            odor_intensity=odor_intensity or None,
            symptoms=",".join(symptoms) if symptoms else None,
            water_ml=water_ml or None,
            observations=observations or None,
        )
        svc.update(record_id, form)
        return RedirectResponse("/urologia?msg=Registo+atualizado+com+sucesso", status_code=303)
    except Exception as exc:
        record = svc.get_by_id(record_id)
        return templates.TemplateResponse(
            "urinary/form.html",
            {
                "request": request,
                "active_page": "urinary",
                "record": record,
                "quantities": QUANTITIES,
                "colors": COLORS,
                "odors": ODORS,
                "symptoms_options": SYMPTOMS,
                "water_amounts": WATER_AMOUNTS,
                "now": recorded_at,
                "selected_symptoms": symptoms,
                "errors": [str(exc)],
            },
            status_code=422,
        )


@router.post("/{record_id}/eliminar")
def uri_delete(record_id: int, svc: UrinaryService = Depends(_svc)):
    svc.delete(record_id)
    return RedirectResponse("/urologia?msg=Registo+eliminado", status_code=303)


@router.get("/graficos", response_class=HTMLResponse)
def uri_charts(request: Request, period: str = "month", svc: UrinaryService = Depends(_svc)):
    chart_data = svc.get_chart_data(period)
    return templates.TemplateResponse(
        "urinary/charts.html",
        {
            "request": request,
            "active_page": "urinary",
            "chart_data": chart_data,
            "period": period,
        },
    )


@router.get("/exportar/csv")
def uri_export_csv(svc: UrinaryService = Depends(_svc)):
    content = svc.export_csv()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=urologia.csv"},
    )


@router.get("/exportar/json")
def uri_export_json(svc: UrinaryService = Depends(_svc)):
    content = svc.export_json()
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=urologia.json"},
    )
