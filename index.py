import os
import sys
from pathlib import Path

# Add the project root and backend/app directory to sys.path
# This ensures that both package-style and flat-style imports work
root_dir = Path(__file__).parent.absolute()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

backend_app_dir = root_dir / "backend" / "app"
if str(backend_app_dir) not in sys.path:
    sys.path.insert(0, str(backend_app_dir))

print(f"Index.py: Root Dir: {root_dir}")
print(f"Index.py: sys.path: {sys.path}")

try:
    # Attempt 1: Import via the full package path
    print("Index.py: Attempting import from backend.app.main")
    from backend.app.main import app
except Exception as e1:
    print(f"Index.py: Attempt 1 failed: {e1}")
    try:
        # Attempt 2: Import directly if backend/app is in path
        print("Index.py: Attempting import from main (flat)")
        import main
        app = main.app
    except Exception as e2:
        print(f"Index.py: Attempt 2 failed: {e2}")
        raise ImportError(f"Could not import FastAPI 'app'. Errors: {e1}, {e2}")

# Vercel looks for 'app' in this module
# By assigning it here, we ensure it's exposed
app = app
