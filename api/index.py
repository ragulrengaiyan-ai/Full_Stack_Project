import os
import sys
from pathlib import Path

# Vercel runs from the root. Add backend/app to path for imports.
root_dir = Path(__file__).parent.parent.absolute()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

backend_app_dir = root_dir / "backend" / "app"
if str(backend_app_dir) not in sys.path:
    sys.path.insert(0, str(backend_app_dir))

try:
    # Standard package-style import
    from backend.app.main import app
except Exception as e:
    print(f"API Bridge: Import failed, trying direct: {e}")
    try:
        # Flat import if path is set
        import main
        app = main.app
    except Exception as e2:
        raise ImportError(f"API Bridge: Could not import FastAPI app. Errors: {e}, {e2}")

# Vercel Python runtime expects the app instance to be available as a variable
app = app
