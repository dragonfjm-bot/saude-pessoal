from datetime import date, datetime, timedelta

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import APP_NAME, STATIC_DIR, TEMPLATES_DIR
from app.database import get_session, init_db
from app.domains.blood_pressure.router import router as bp_router
from app.domains.blood_pressure.service import BloodPressureService
from app.domains.urinary.router import router as uri_router
from app.domains.urinary.service import UrinaryService
from app.domains.weight.router import router as wt_router
from app.domains.weight.service import WeightService

app = FastAPI(title=APP_NAME, docs_url=None, redoc_url=None)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
templates.env.globals["now"] = datetime.now

app.include_router(bp_router)
app.include_router(uri_router)
app.include_router(wt_router)


@app.on_event("startup")
def startup():
    init_db()


@app.get("/exportar", response_class=HTMLResponse)
def export_page(request: Request):
    return templates.TemplateResponse(
        "export.html", {"request": request, "active_page": "export"}
    )


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_session)):
    bp_svc = BloodPressureService(db)
    uri_svc = UrinaryService(db)
    wt_svc = WeightService(db)

    latest_bp = bp_svc.get_latest()
    latest_wt = wt_svc.get_latest()
    today_uri_count = uri_svc.get_today_count()
    bp_week_stats = bp_svc.get_week_stats()
    wt_trend = wt_svc.get_trend()
    recent_bp = bp_svc.list(page=1, per_page=5)[0]

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "active_page": "dashboard",
            "latest_bp": latest_bp,
            "latest_wt": latest_wt,
            "today_uri_count": today_uri_count,
            "bp_week_stats": bp_week_stats,
            "wt_trend": wt_trend,
            "recent_bp": recent_bp,
            "classify_bp": bp_svc.classify,
        },
    )
