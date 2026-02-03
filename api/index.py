import os
import sys
from pathlib import Path

# Add the project root to sys.path
# On Vercel, the function runs with the root as the CWD
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

try:
    # Try importing from the package
    from backend.app.main import app
except Exception as e:
    # Diagnostic fallback
    import traceback
    print(f"IMPORT ERROR: {e}")
    traceback.print_exc()
    
    # Create a dummy app to at least show something if imports fail
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/api/debug")
    async def debug():
        return {
            "error": str(e),
            "sys_path": sys.path,
            "root_dir": root_dir,
            "cwd": os.getcwd(),
            "files": os.listdir(root_dir) if os.path.exists(root_dir) else "not found"
        }

# Vercel needs 'app' to be available
app = app
