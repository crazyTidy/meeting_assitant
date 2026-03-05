from fastapi import FastAPI
from app.core.config import settings

app = FastAPI()

@app.get("/test-config")
def test_config():
    return {"dev_mode": settings.DEV_MODE, "type": str(type(settings.DEV_MODE))}
