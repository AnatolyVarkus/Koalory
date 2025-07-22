from fastapi import FastAPI
from app.core.config import settings
from app.api import auth_router, register_router, form_router
from app.core.wrapper import CustomRoute

app = FastAPI(
    title="Koalory API",
    version="1.0.0",
    debug=settings.DEBUG,
    root_path="/api"
)

app.include_router(auth_router)
app.include_router(register_router)
app.include_router(form_router)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
