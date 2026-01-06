import sys
import os

# Add the 'backend' folder to sys.path so imports like 'from app.database import ...' work
# This assumes the structure is:
# project_root/
#   api/index.py
#   backend/app/
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root, 'backend'))

from app.main import app

# This is required for Vercel to find the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
