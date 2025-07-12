from fastapi import FastAPI
from app.api import auth_router, register_router
from app.core.config import settings
from app.core.wrapper import CustomRoute

app = FastAPI(
    title="Koalory API",
    version="1.0.0",
    debug=settings.DEBUG
)

# Include your API routes
app.router.route_class = CustomRoute
app.include_router(auth_router)
app.include_router(register_router)



@app.get("/health")
def healthcheck():
    return {"status": "ok"}
