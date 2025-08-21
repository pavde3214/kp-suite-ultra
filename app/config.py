import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_URL = os.getenv("DB_URL", f"sqlite:///{(BASE_DIR / 'kp.db').as_posix()}")

DOCS_DIR = BASE_DIR / "storage" / "docs"
TEMPLATES_DIR = BASE_DIR / "storage" / "templates" / "contracts"
STATIC_DIR = BASE_DIR / "app" / "web" / "static"
HTML_TPL_DIR = BASE_DIR / "app" / "web" / "templates"

for p in (DOCS_DIR, TEMPLATES_DIR, STATIC_DIR, HTML_TPL_DIR):
    p.mkdir(parents=True, exist_ok=True)

CONTRACT_NUMBER_MASK = os.getenv("CONTRACT_NUMBER_MASK", "DOG-{YYYY}-{SEQ:04d}")
PROPOSAL_NUMBER_MASK = os.getenv("PROPOSAL_NUMBER_MASK", "KP-{YYYY}-{SEQ:04d}")

ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "admin")
