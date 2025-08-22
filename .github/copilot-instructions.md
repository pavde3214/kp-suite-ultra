# KP Suite ULTRA

KP Suite ULTRA is a FastAPI-based web application for managing commercial proposals (КП = коммерческое предложение), contracts, customers, and materials. It is primarily a business application for HVAC contractors with Russian language interface and documentation generation capabilities.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Bootstrap, build, and run the repository:
- **NEVER CANCEL**: All build steps complete quickly (under 60 seconds total). Set timeout to 120+ seconds to be safe.
- `python3 -m venv .venv` -- takes ~3 seconds
- `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
- `python -m pip install --upgrade pip` -- takes ~2 seconds (may timeout due to network limitations)
- `python -m pip install -r requirements.txt` -- takes ~30 seconds. NEVER CANCEL. May fail due to network timeouts in restrictive environments.
- `python seed_catalog.py` -- (optional) seeds sample materials data, takes <1 second
- `python make_templates.py` -- (optional) creates document templates, takes <1 second

### Common network issues:
- **pip install may timeout** in restricted network environments with message "Read timed out" - this is an environment limitation, not a code issue
- If pip installation fails due to network timeout, the application may still work if dependencies were previously installed

### Run the application:
- **ALWAYS run the bootstrapping steps first.**
- `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` -- starts in ~10 seconds
- Default URL: http://localhost:8000/
- Health check endpoint: http://localhost:8000/health

### Python syntax validation:
- `python -m py_compile app/main.py` -- validates syntax of main application file
- `find app/ -name "*.py" -exec python -m py_compile {} \;` -- validates all Python files

## Validation

- **ALWAYS manually test key user workflows** after making changes to ensure the application works correctly.
- **Key test scenarios to validate:**
  1. Application starts successfully (http://localhost:8000/health returns {"status":"ok"})
  2. Main page loads (http://localhost:8000/ returns 200)
  3. Customer management works (http://localhost:8000/customers returns 200)
  4. Materials API works (http://localhost:8000/api/v1/materials returns JSON array)
  5. Create a test customer via POST to /customers/create
  6. Seed data populates correctly with `python seed_catalog.py`
- **No automated tests exist** - all validation must be done manually through the web interface or API calls.
- **No linting tools are configured** - use `python -m py_compile` for basic syntax validation.

## Common Tasks

The following are outputs from frequently run commands. Reference them instead of viewing, searching, or running bash commands to save time.

### Repository structure
```
.
├── app/                    # Main application code
│   ├── main.py            # FastAPI application entry point
│   ├── config.py          # Configuration settings
│   ├── models/            # SQLAlchemy models
│   ├── api/               # API routers
│   ├── db/                # Database configuration
│   ├── services/          # Business logic
│   └── web/               # Static files and templates
├── storage/               # Generated during setup
│   ├── docs/              # Generated documents
│   └── templates/         # Document templates
├── requirements.txt       # Python dependencies
├── seed_catalog.py        # Sample data seeder
├── make_templates.py      # Document template generator
├── setup_everything.bat   # Windows setup script
├── run_kp.bat            # Windows launcher
└── kp.db                 # SQLite database (generated)
```

### Key files and dependencies
- **Main entry point**: `app/main.py` - FastAPI application with all routes
- **Configuration**: `app/config.py` - Database URL, paths, admin credentials
- **Database**: SQLite by default (`kp.db`), configurable via DB_URL environment variable
- **Dependencies**: FastAPI, SQLAlchemy 2.0+, Pydantic 2+, Jinja2, python-docx, xhtml2pdf
- **Templates**: HTML templates in `app/web/templates/`, DOCX templates in `storage/templates/contracts/`

### Common commands and their expected timing
- `python3 -m venv .venv` -- ~3 seconds
- `python -m pip install --upgrade pip` -- ~2 seconds (may timeout in restricted networks)
- `python -m pip install -r requirements.txt` -- ~30 seconds (may timeout in restricted networks)
- `python seed_catalog.py` -- <1 second (optional)
- `python make_templates.py` -- <1 second (optional)
- `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload` -- starts in ~10 seconds

### Environment and dependencies
- **Python version**: 3.12+ required
- **Platform**: Cross-platform (Linux/Mac/Windows)
- **Database**: SQLite (no separate installation required)
- **No build step required** - Python application runs directly

### Database and data
- Uses SQLite database (`kp.db`) created automatically on first run
- Includes tables: customers, proposals, materials, estimates, contracts, etc.
- Sample data available via `python seed_catalog.py` (16 HVAC materials/services)
- Admin credentials: username="admin", password="admin" (configurable via environment)

### Key application features
- **Customer management**: Create, view, edit customer information
- **Commercial proposals (КП)**: Create detailed proposals with sections and items
- **Materials catalog**: Searchable database of materials with prices
- **Contract generation**: Generate contracts in HTML and DOCX formats
- **Document management**: Upload and manage document templates
- **PDF export**: Export proposals and contracts as PDF files

### API endpoints (for testing)
- `GET /health` - Health check (returns {"status":"ok"})
- `GET /api/v1/materials` - List all materials
- `GET /api/v1/materials?q=search` - Search materials
- `POST /customers/create` - Create new customer
- UI available at root URL with full functionality

### Known working fixes applied
- Added missing import `from fastapi.templating import Jinja2Templates` in `app/main.py`
- Added missing import `from fastapi.responses import FileResponse` in `app/main.py`  
- Fixed import in `seed_catalog.py`: `from app.db.session import SessionLocal`
- All imports and dependencies are now correctly configured

### Troubleshooting
- **Import errors**: Ensure virtual environment is activated and dependencies installed
- **Network timeouts during pip install**: Common in restricted environments - try alternative package sources or use pre-installed dependencies
- **Database errors**: Database and tables are created automatically on first startup
- **Template errors**: Run `python make_templates.py` to create missing document templates
- **Permission errors**: Ensure storage directories exist (created automatically by config.py)
- **Port conflicts**: Use different port with `--port 8001` if 8000 is occupied

## CI/CD
- **GitHub Actions**: `.github/workflows/jekyll-docker.yml` exists but is for Jekyll (legacy/unused)
- **No automated testing pipeline** - all validation is manual
- **No deployment configuration** - application runs locally only

## Working with the codebase
- **Main application logic**: Located in `app/main.py` with all routes and handlers
- **Database models**: In `app/models/` directory
- **API routes**: Organized in `app/api/routers/` by feature
- **HTML templates**: In `app/web/templates/` using Jinja2
- **Business logic**: In `app/services/` for calculations, document generation
- **Configuration**: Centralized in `app/config.py`

Always validate changes by running the application and testing key user scenarios manually through the web interface.