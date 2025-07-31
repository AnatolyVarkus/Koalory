from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse
from fastapi import HTTPException
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Callable
import json
import inspect

class CustomRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request):
            try:
                response = await original_route_handler(request)

                if inspect.isawaitable(response):
                    response = await response

                body = getattr(response, "body", None)
                if body is None:
                    decoded_body = None
                else:
                    decoded_body = json.loads(body)

                return JSONResponse(
                    status_code=response.status_code,
                    content={
                        "success": True,
                        "data": decoded_body,
                        "error": None
                    }
                )

            except (HTTPException, StarletteHTTPException) as http_exc:
                return JSONResponse(
                    status_code=http_exc.status_code,
                    content={
                        "success": False,
                        "data": None,
                        "error": http_exc.detail
                    }
                )
            
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "data": None,
                        "error": str(e)
                    }
                )

        return custom_route_handler
