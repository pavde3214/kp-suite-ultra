# KP Suite ULTRA
KP Suite ULTRA is a Python FastAPI web application for HVAC commercial proposals and estimates management. The application allows creating customer records, generating commercial proposals (КП), managing materials catalog, and producing contracts in DOCX format.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively
- Bootstrap the environment and dependencies:
  - `python3 -m venv .venv` -- takes 3 seconds
  - `source .venv/bin/activate` (Linux/Mac) or `.venv\Scripts\activate` (Windows)
  - `python -m pip install --upgrade pip` -- takes 3 seconds
  - `python -m pip install -r requirements.txt` -- takes 30 seconds. NEVER CANCEL. Set timeout to 60+ seconds.
- Initialize database and run the application:
  - `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` -- starts in 2-3 seconds
  - Access at http://localhost:8000
- Seed catalog with test data:
  - `python seed_catalog.py` -- takes 1 second, adds 14 material/service items

## Validation
- ALWAYS test the full application startup after making changes by:
  1. Starting the server with uvicorn (ensure it shows "Application startup complete")
  2. Testing the health endpoint: `curl http://localhost:8000/health` should return `{"status":"ok"}`
  3. Testing the main page: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/` should return `200`
- ALWAYS run through at least one complete end-to-end scenario after making changes:
  - Navigate to http://localhost:8000 and verify the homepage loads
  - Click "Клиенты" (Customers) and verify the customer list displays
  - Click "КП" and verify the proposals list displays
  - Click "Материалы" (Materials) and verify the materials page loads
- Test core functionality workflows:
  - Create a new customer through the customers page form
  - Create a new proposal (КП) for a customer
  - View existing proposals in the table
- Database operations work correctly:
  - Application auto-creates SQLite database tables on startup
  - Seeding script populates materials catalog successfully

## Common Commands and Expected Times
- **Virtual environment creation**: `python3 -m venv .venv` (3 seconds)
- **Pip upgrade**: `python -m pip install --upgrade pip` (3 seconds) 
- **Dependencies installation**: `python -m pip install -r requirements.txt` (30 seconds) - NEVER CANCEL, set timeout to 60+ seconds
- **Application startup**: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000` (2-3 seconds to start)
- **Catalog seeding**: `python seed_catalog.py` (1 second)

## Repository Structure
### Key Directories
- `app/` - Main FastAPI application code
  - `main.py` - FastAPI application entry point with routes
  - `models/` - SQLAlchemy database models
  - `db/` - Database configuration and initialization
  - `api/routers/` - API endpoint routers
  - `web/templates/` - Jinja2 HTML templates
  - `web/static/` - Static files (CSS, JS, images)
  - `services/` - Business logic services
- `.venv/` - Python virtual environment (auto-created)
- `storage/` - File storage for documents and templates

### Key Files
- `requirements.txt` - Python dependencies (FastAPI, SQLAlchemy 2.0+, etc.)
- `run_kp.bat` - Windows launcher script (creates venv and runs app)
- `setup_everything.bat` - Windows full setup script
- `seed_catalog.py` - Populates materials catalog with test data
- `kp.db` - SQLite database file (auto-created)

## Dependencies and SDKs
- **Python 3.12+** required
- **Virtual environment** - always use `.venv` directory
- **Core dependencies** (installed via pip):
  - FastAPI - web framework
  - Uvicorn - ASGI server  
  - SQLAlchemy 2.0+ - database ORM
  - Pydantic 2+ - data validation
  - Jinja2 - HTML templating
  - python-docx - Word document generation
  - xhtml2pdf - PDF generation
  - openpyxl - Excel file handling

## Database and Configuration
- **Database**: SQLite (file: `kp.db`) - auto-created and initialized
- **Tables created on startup**: categories, customers, estimates, materials, proposals, etc.
- **No manual database setup required** - application handles initialization
- **Default configuration**: Development mode with auto-reload enabled
- **Default admin credentials**: admin/admin (configurable via environment)

## Common Issues and Solutions
- **Missing import error for Jinja2Templates**: Add `from fastapi.templating import Jinja2Templates` to imports
- **Virtual environment path issues**: Linux uses `.venv/bin/activate`, Windows uses `.venv\Scripts\activate`
- **Import errors in scripts**: Use full import paths like `from app.db.session import SessionLocal`
- **Port conflicts**: Application runs on port 8000 by default

## Testing and Development Workflow
1. **Setup**: Create venv, install dependencies (60 seconds total)
2. **Development**: Run app with auto-reload: `python -m uvicorn app.main:app --reload`
3. **Testing**: Access http://localhost:8000, test key workflows manually
4. **Data**: Run `python seed_catalog.py` to populate test data
5. **Validation**: Always test startup, health endpoint, and core pages after changes

## Application Features
- **Customer Management**: Create and manage customer records with addresses
- **Commercial Proposals (КП)**: Create structured proposals with sections and items
- **Materials Catalog**: Manage equipment, materials, and services with pricing
- **Contract Generation**: Generate DOCX contracts from proposals
- **PDF Export**: Export proposals to PDF format
- **Auto-numbering**: Automatic numbering for proposals and contracts
- **Multi-language**: Russian interface (HVAC/КП terminology)

## Important Notes
- This is a Russian-language HVAC business application
- КП = Коммерческое предложение (Commercial Proposal)
- Application includes HVAC-specific terminology and workflows
- No test suite exists - rely on manual testing scenarios
- No linting tools configured by default
- Database schema is auto-managed by SQLAlchemy