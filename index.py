import sys
from pathlib import Path

# Add the project root and app directory to sys.path
root_dir = Path(__file__).parent
sys.path.append(str(root_dir))
sys.path.append(str(root_dir / "backend" / "app"))

try:
    from backend.app.main import app
except ImportError:
    # Fallback for local testing or different launch contexts
    from main import app

# Vercel needs the 'app' variable to be available at the module level
# We have it already through the import
