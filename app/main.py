from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi
from app.core.config import settings
from app.api import auth_router, register_router, form_router, payment_router, story_request_router, verification_router
import re
import inspect
from fastapi.middleware.cors import CORSMiddleware
from app.core.wrapper import CustomRoute
from app.core.celery_app import celery

app = FastAPI(
    title="Koalory API",
    version="1.0.0",
    debug=settings.DEBUG,
    root_path="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # разрешить ВСЕМ
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(register_router)
app.include_router(form_router)
app.include_router(payment_router)
app.include_router(story_request_router)
app.include_router(verification_router)

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="My Auth API",
#         version="1.0",
#         description="An API with an Authorize Button",
#         routes=app.routes,
#     )
#     openapi_schema["components"]["securitySchemes"] = {
#         "Bearer Auth": {
#             "type": "apiKey",
#             "in": "header",
#             "name": "Authorization",
#             "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
#         }
#     }
#     # Get all routes where jwt_optional() or jwt_required
#     api_router = [route for route in app.routes if isinstance(route, APIRoute)]
#     for route in api_router:
#         path = getattr(route, "path")
#         endpoint = getattr(route, "endpoint")
#         methods = [method.lower() for method in getattr(route, "methods")]
#         for method in methods:
#             # access_token
#             if (
#                     re.search("jwt_required", inspect.getsource(endpoint)) or
#                     re.search("fresh_jwt_required", inspect.getsource(endpoint)) or
#                     re.search("jwt_optional", inspect.getsource(endpoint))
#             ):
#                 openapi_schema["paths"][path][method]["security"] = [
#                     {
#                         "Bearer Auth": []
#                     }
#                 ]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

@app.get("/health")
def healthcheck():
    return {"status": "ok"}

# app.openapi = custom_openapi