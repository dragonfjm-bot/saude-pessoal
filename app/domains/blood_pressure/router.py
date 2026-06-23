from datetime import date, datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import ITEMS_PER_PAGE, TEMPLATES_DIR
from app.database import get_session
from app.domains.blood_pressure.schemas import BP_CONTEXTS, BloodPressureForm
from app.domains.blood_pressure.service import BloodPressureService

router = APIRouter(prefix="/tensao-arterial", tags=["blood_pressure"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def _svc(db: Session = Depends(get_session)) -> BloodPressureService:
    return BloodPressureService(db)


@router.get("", response_class=HTMLResponse)
def bp_list(
    request: Request,
    page: int = 1,
    date_from: date | None = None,
    date_to: date | None = None,
    svc: BloodPressureService = Depends(_svc),
):
    records, total = svc.list(page=page, per_page=ITEMS_PER_PAGE, date_from=date_from, date_to=date_to)
    total_pages = max(1, -(-total // ITEMS_PER_PAGE))
    return templates.TemplateResponse(
        "blood_pressure/list.html",
        {
            "request": request,
            "active_page": "blood_pressure",
            "records": records,
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "date_from": date_from,
            "date_to": date_to,
            "classify": svc.classify,
            "msg": request.query_params.get("msg"),
        },
    )


@router.get("/novo", response_class=HTMLResponse)
def bp_new(request: Request):
    return templates.TemplateResponse(
        "blood_pressure/form.html",
        {
            "request": request,
            "active_page": "blood_pressure",
            "record": None,
            "contexts": BP_CONTEXTS,
            "now": datetime.now().strftime("%Y-%m-%dT%H:%M"),
            "errors": [],
        },
    )


@router.post("/novo")
def bp_create(
    request: Request,
    measured_at: str = Form(...),
    systolic: int = Form(...),
    diastolic: int = Form(...),
    heart_rate: str = Form(""),
    context: str = Form(""),
    observations: str = Form(""),
    svc: BloodPressureService = Depends(_svc),
):
    try:
        form = BloodPressureForm(
            measured_at=datetime.fromisoformat(measured_at),
            systolic=systolic,
            diastolic=diastolic,
            heart_rate=heart_rate or None,
            context=context or None,
            observations=observations or None,
        )
        svc.create(form)
        return RedirectResponse("/tensao-arterial?msg=Registo+criado+com+sucesso", status_code=303)
    except Exception as exc:
        return templates.TemplateResponse(
            "blood_pressure/form.html",
            {
                "request": request,
                "active_page": "blood_pressure",
                "record": None,
                "contexts": BP_CONTEXTS,
                "now": measured_at,
                "errors": [str(exc)],
            },
            status_code=422,
        )


@router.get("/{record_id}/editar", response_class=HTMLResponse)
def bp_edit(record_id: int, request: Request, svc: BloodPressureService = Depends(_svc)):
    record = svc.get_by_id(record_id)
    if not record:
        return RedirectResponse("/tensao-arterial")
    return templates.TemplateResponse(
        "blood_pressure/form.html",
        {
            "request": request,
            "active_page": "blood_pressure",
            "record": record,
            "contexts": BP_CONTEXTS,
            "now": record.measured_at.strftime("%Y-%m-%dT%H:%M"),
            "errors": [],
        },
    )


@router.post("/{record_id}/editar")
def bp_update(
    record_id: int,
    request: Request,
    measured_at: str = Form(...),
    systolic: int = Form(...),
    diastolic: int = Form(...),
    heart_rate: str = Form(""),
    context: str = Form(""),
    observations: str = Form(""),
    svc: BloodPressureService = Depends(_svc),
):
    try:
        form = BloodPressureForm(
            measured_at=datetime.fromisoformat(measured_at),
            systolic=systolic,
            diastolic=diastolic,
            heart_rate=heart_rate or None,
            context=context or None,
            observations=observations or None,
        )
        svc.update(record_id, form)
        return RedirectResponse("/tensao-arterial?msg=Registo+atualizado+com+sucesso", status_code=303)
    except Exception as exc:
        record = svc.get_by_id(record_id)
        return templates.TemplateResponse(
            "blood_pressure/form.html",
            {
                "request": request,
                "active_page": "blood_pressure",
                "record": record,
                "contexts": BP_CONTEXTS,
                "now": measured_at,
                "errors": [str(exc)],
            },
            status_code=422,
        )


@router.post("/{record_id}/eliminar")
def bp_delete(record_id: int, svc: BloodPressureService = Depends(_svc)):
    svc.delete(record_id)
    return RedirectResponse("/tensao-arterial?msg=Registo+eliminado", status_code=303)


@router.get("/graficos", response_class=HTMLResponse)
def bp_charts(request: Request, period: str = "month", svc: BloodPressureService = Depends(_svc)):
    chart_data = svc.get_chart_data(period)
    return templates.TemplateResponse(
        "blood_pressure/charts.html",
        {
            "request": request,
            "active_page": "blood_pressure",
            "chart_data": chart_data,
            "period": period,
        },
    )


@router.get("/exportar/csv")
def bp_export_csv(svc: BloodPressureService = Depends(_svc)):
    content = svc.export_csv()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=tensao_arterial.csv"},
    )


@router.get("/exportar/json")
def bp_export_json(svc: BloodPressureService = Depends(_svc)):
    content = svc.export_json()
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=tensao_arterial.json"},
    )
