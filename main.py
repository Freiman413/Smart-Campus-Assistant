
import uvicorn
import os
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import status
from datetime import datetime
from dotenv import load_dotenv
from router import pages
from router import lecturer_dashboard
from router import admin
from data_base.db import init_database
from ai_server import main_server

load_dotenv()
init_database()
app = FastAPI()
APP_NAME = os.environ["APP_NAME"]
HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])
DEBUG_MODE = os.environ["DEBUG"].lower() == "true"
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": exc.status_code,
            "message": exc.detail,
            "path": request.url.path,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "validation_error",
            "message": "Invalid request data.",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": 500,
            "message": "Internal server error.",
            "path": request.url.path,
        },
    )




app.include_router(pages.router)
app.include_router(lecturer_dashboard.router)
app.include_router(admin.router)
app.include_router(main_server.router)

if __name__ == "__main__":
    uvicorn.run(app=APP_NAME, host=HOST, port=PORT, reload=DEBUG_MODE)
    