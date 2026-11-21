"""Entry point:  python main.py   ->  http://localhost:4000/docs"""
import uvicorn

from app.config import settings
from app.main import app  # noqa: F401  (re-exported for `uvicorn main:app`)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=settings.port)
