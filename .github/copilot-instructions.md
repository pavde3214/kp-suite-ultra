# GitHub Copilot Instructions for KP Suite ULTRA

**ALWAYS follow these instructions first and fallback to additional search or bash commands only when the information here is incomplete or found to be in error.**

## Project Overview

KP Suite ULTRA is a Python FastAPI web application for creating HVAC/construction proposals and estimates. The application uses SQLAlchemy for database ORM, Uvicorn as the ASGI server, and includes a Russian language web interface for managing customers, materials, proposals, and generating documents.

## Technology Stack
- **Backend**: Python 3.12.3 + FastAPI + SQLAlchemy 2.0 + Uvicorn
- **Database**: SQLite with auto-initialization (14 tables)
- **Frontend**: HTML templates with Jinja2, CSS, basic JavaScript
- **Dependencies**: 48 packages including python-docx, xhtml2pdf, openpyxl for document generation

## Critical Setup and Build Instructions

### 1. Environment Setup
**NEVER CANCEL - Setup can take 30-180 seconds depending on network. Set timeout to 300+ seconds.**

```bash
# Create and activate virtual environment (required on Linux)
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (~30 seconds normally, up to 180 seconds with network issues)
pip install -r requirements.txt --timeout=300 --retries=3
```

**Common Network Issues:**
- If `pip install` fails with timeout errors: **This is common due to network/firewall limitations**
- **Workaround**: Retry the command 2-3 times
- **Alternative**: Use `pip install -r requirements.txt --timeout=600` for slower networks

**Windows Alternative** (if using Windows environment):
```cmd
run_kp.bat
```

**Skip pip upgrade** - The default pip version is sufficient. Upgrading can cause network timeout issues.

### 2. Database Initialization and Seeding
**Time: ~0.3 seconds**

```bash
# Activate virtual environment
source .venv/bin/activate

# Seed database with sample materials (optional but recommended)
python seed_catalog.py
```

### 3. Running the Application
**NEVER CANCEL - Server startup takes ~3 seconds. Set timeout to 30+ seconds.**

```bash
# Activate virtual environment
source .venv/bin/activate

# Start development server with auto-reload
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# OR start without auto-reload (more stable for testing)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Application will be available at**: http://localhost:8000

## Validation and Testing

### Manual Validation Scenarios
**ALWAYS run these validation steps after making changes:**

1. **Basic Server Test**:
   ```bash
   curl -s http://localhost:8000/ | head -10
   # Should return HTML with "KP Suite ULTRA" title
   ```

2. **Core User Workflow**:
   - Navigate to http://localhost:8000 (main page should load)
   - Click "Клиенты" (Customers) - should show customer list
   - Click "Материалы" (Materials) - should show materials list with seeded data
   - Click "КП" (Proposals) - should show proposals interface

3. **Database Validation**:
   ```bash
   # Check if database was created and has tables
   ls -la kp.db  # Should exist and be >70KB if seeded
   ```

### API Testing
```bash
# Test basic endpoints
curl -s http://localhost:8000/customers | grep -q "html" && echo "Customers page OK"
curl -s http://localhost:8000/materials | grep -q "html" && echo "Materials page OK"
```

## Code Structure and Key Locations

### Application Structure
```
app/
├── main.py              # Main FastAPI application entry point
├── config.py            # Configuration settings
├── api/routers/         # API route handlers (customers, materials, etc.)
├── models/              # SQLAlchemy database models
├── schemas/             # Pydantic schemas for validation
├── services/            # Business logic services
├── db/                  # Database configuration and initialization
└── web/templates/       # Jinja2 HTML templates
```

### Important Files to Know
- **app/main.py**: Main application file with route definitions
- **requirements.txt**: Python dependencies (11 lines)
- **seed_catalog.py**: Database seeding script for sample materials
- **app/db/init_db.py**: Database initialization logic
- **app/models/**: Database models for Customer, Estimate, Proposal, Material
- **setup_everything.bat**: Windows setup script (reference only)

### Key Routes and Functionality
- `/` - Main dashboard
- `/customers` - Customer management
- `/materials` - Materials catalog
- `/proposals` - Proposal/estimate creation
- `/documents` - Document management

## Common Tasks

### Development Workflow
1. **Always activate virtual environment first**:
   ```bash
   source .venv/bin/activate
   ```

2. **Start development server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Test your changes manually** using the validation scenarios above

### Adding New Dependencies
```bash
source .venv/bin/activate
pip install <package-name> --timeout=300 --retries=3
pip freeze > requirements.txt
```

**Note**: Network timeouts are common. If pip install fails, document it as "fails due to network limitations" and continue with existing environment.

### Database Operations
```bash
# Reset and reseed database
rm -f kp.db
python seed_catalog.py
```

## Known Issues and Workarounds

### Fixed Issues (Already Resolved)
- **Import Issue**: `Jinja2Templates` import was missing from `app/main.py` - FIXED
- **Seed Script**: Import path in `seed_catalog.py` was incorrect - FIXED

### Current Known Issues
- **Template Error**: Some proposal edit pages have SQLAlchemy session errors (DetachedInstanceError)
- **Workaround**: Basic functionality works, proposal creation may have edge cases
- **Impact**: Does not affect main development workflow or basic testing

### No Build Process Required
- This is a pure Python application - no compilation or build step needed
- No linting tools are configured (flake8, black, pytest not installed)
- No CI/CD pipeline exists beyond basic Jekyll workflow

## Timing Expectations and Warnings

**CRITICAL: NEVER CANCEL these operations**

| Operation | Expected Time | Timeout Setting | Notes |
|-----------|---------------|-----------------|-------|
| `python3 -m venv .venv` | ~3 seconds | 30 seconds | Virtual environment creation |
| `pip install -r requirements.txt` | 30-180 seconds | 300+ seconds | **May fail due to network issues** |
| `python seed_catalog.py` | ~0.3 seconds | 30 seconds | Database seeding |
| `uvicorn app.main:app --reload` | ~3 seconds | 30 seconds | Server startup |
| Server startup complete | ~3 seconds | 30 seconds | Application initialization |

**Network Issue Handling:**
- **pip install timeouts**: Common in CI/sandboxed environments
- **Solution**: Retry command 2-3 times with `--timeout=600 --retries=3`
- **Alternative**: Document "pip install fails due to network limitations" and continue with manual testing if dependencies exist

## File Locations for Common Changes

### When modifying API routes:
- Check `app/api/routers/` for existing route files
- Update `app/main.py` to include new routers

### When modifying database models:
- Update files in `app/models/`
- Consider running database migrations (not automated)

### When modifying templates:
- Edit files in `app/web/templates/`
- Template base is `layout.html`

### When adding new business logic:
- Add services to `app/services/`
- Follow existing patterns in `app/services/payments.py`, etc.

## Troubleshooting

### If server won't start:
1. Check virtual environment is activated
2. Verify dependencies exist: `pip list | wc -l` should show 30+ packages (if network install worked)
3. **If dependencies missing due to network issues**: Document as "Dependencies not installable due to network limitations"
4. Check for Python syntax errors: `python -c "from app.main import app"`
5. Check requirements.txt exists and is readable

### If database issues:
1. Delete database: `rm -f kp.db`
2. Restart server - auto-initialization will recreate tables
3. Reseed: `python seed_catalog.py`

### If import errors:
1. Check virtual environment: `which python` should show `.venv` path
2. Reinstall dependencies: `pip install -r requirements.txt`

## Important: No Tests or Linting
- **No test suite exists** - rely on manual validation scenarios above
- **No linting configured** - check code manually for obvious syntax errors
- **No automated CI/CD** - manual testing is critical

Always test your changes thoroughly using the manual validation scenarios before considering them complete.