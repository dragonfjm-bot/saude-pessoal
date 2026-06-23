import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "app" / "templates"

DATA_DIR.mkdir(exist_ok=True)

_default_db = f"sqlite:///{DATA_DIR / 'saude.db'}"
DATABASE_URL = os.environ.get("DATABASE_URL", _default_db)

# Render/Heroku provide postgres:// but SQLAlchemy requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

APP_NAME = "Saúde Pessoal"
APP_VERSION = "1.0.0"
ITEMS_PER_PAGE = 20
