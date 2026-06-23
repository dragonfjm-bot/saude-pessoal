from datetime import date, datetime

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import ITEMS_PER_PAGE, TEMPLATES_DIR
from app.database import get_session
from app.domains.weight.schemas import WeightForm
from app.domains.weight.service import WeightService

router = APIRouter(prefix="/peso", tags=["weight"])
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def _svc(db: Session = Depends(get_session)) -> WeightService:
    return WeightService(db)


@router.get("", response_class=HTMLResponse)
def wt_list(
    request: Request,
    page: int = 1,
    date_from: date | None = None,
    date_to: date | None = None,
    svc: WeightService = Depends(_svc),
):
    records, total = svc.list(page=page, per_page=ITEMS_PER_PAGE, date_from=date_from, date_to=date_to)
    total_pages = max(1, -(-total // ITEMS_PER_PAGE))
    return templates.TemplateResponse(
        "weight/list.html",
        {
            "request": request,
            "active_page": "weight",
            "records": records,
            "total": total,
            "page": page,
            "total_pages": total_pages,
            "date_from": date_from,
            "date_to": date_to,
            "msg": request.query_params.get("msg"),
        },
    )


@router.get("/novo", response_class=HTMLResponse)
def wt_new(request: Request):
    return templates.TemplateResponse(
        "weight/form.html",
        {
            "request": request,
            "active_page": "weight",
            "record": None,
            "now": datetime.now().strftime("%Y-%m-%dT%H:%M"),
            "errors": [],
        },
    )


@router.post("/novo")
def wt_create(
    request: Request,
    measured_at: str = Form(...),
    weight_kg: float = Form(...),
    observations: str = Form(""),
    svc: WeightService = Depends(_svc),
):
    try:
        form = WeightForm(
            measured_at=datetime.fromisoformat(measured_at),
            weight_kg=weight_kg,
            observations=observations or None,
        )
        svc.create(form)
        return RedirectResponse("/peso?msg=Registo+criado+com+sucesso", status_code=303)
    except Exception as exc:
        return templates.TemplateResponse(
            "weight/form.html",
            {
                "request": request,
                "active_page": "weight",
                "record": None,
                "now": measured_at,
                "errors": [str(exc)],
            },
            status_code=422,
        )


@router.get("/{record_id}/editar", response_class=HTMLResponse)
def wt_edit(record_id: int, request: Request, svc: WeightService = Depends(_svc)):
    record = svc.get_by_id(record_id)
    if not record:
        return RedirectResponse("/peso")
    return templates.TemplateResponse(
        "weight/form.html",
        {
            "request": request,
            "active_page": "weight",
            "record": record,
            "now": record.measured_at.strftime("%Y-%m-%dT%H:%M"),
            "errors": [],
        },
    )


@router.post("/{record_id}/editar")
def wt_update(
    record_id: int,
    request: Request,
    measured_at: str = Form(...),
    weight_kg: float = Form(...),
    observations: str = Form(""),
    svc: WeightService = Depends(_svc),
):
    try:
        form = WeightForm(
            measured_at=datetime.fromisoformat(measured_at),
            weight_kg=weight_kg,
            observations=observations or None,
        )
        svc.update(record_id, form)
        return RedirectResponse("/peso?msg=Registo+atualizado+com+sucesso", status_code=303)
    except Exception as exc:
        record = svc.get_by_id(record_id)
        return templates.TemplateResponse(
            "weight/form.html",
            {
                "request": request,
                "active_page": "weight",
                "record": record,
                "now": measured_at,
                "errors": [str(exc)],
            },
            status_code=422,
        )


@router.post("/{record_id}/eliminar")
def wt_delete(record_id: int, svc: WeightService = Depends(_svc)):
    svc.delete(record_id)
    return RedirectResponse("/peso?msg=Registo+eliminado", status_code=303)


@router.get("/graficos", response_class=HTMLResponse)
def wt_charts(request: Request, period: str = "month", svc: WeightService = Depends(_svc)):
    chart_data = svc.get_chart_data(period)
    return templates.TemplateResponse(
        "weight/charts.html",
        {
            "request": request,
            "active_page": "weight",
            "chart_data": chart_data,
            "period": period,
        },
    )


@router.get("/exportar/csv")
def wt_export_csv(svc: WeightService = Depends(_svc)):
    content = svc.export_csv()
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=peso.csv"},
    )


@router.get("/exportar/json")
def wt_export_json(svc: WeightService = Depends(_svc)):
    content = svc.export_json()
    return Response(
        content=content,
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=peso.json"},
    )
