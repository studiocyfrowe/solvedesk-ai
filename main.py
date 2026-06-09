import uvicorn as uv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from solvedesk_cmd.api.routes.crud import router as crud_router
from solvedesk_cmd.api.routes.sync import router as import_router
from solvedesk_cmd.api.routes.search import router as search_router
from solvedesk_cmd.api.routes.explain import router as explain_router
from solvedesk_cmd.api.handlers.auth_handlers import register_auth_handlers

from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(
    title=f"{os.getenv('PROJECT_NAME')}",
    description=f"{os.getenv('PROJECT_DESCRIPTION')}",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_auth_handlers(app)

app.include_router(search_router, prefix="/api", tags=["Search"])
app.include_router(explain_router, prefix="/api", tags=["Explain"])
app.include_router(crud_router, prefix="/api", tags=["CRUD"])
app.include_router(import_router, prefix="/api", tags=["Import / Data Sync"])

if __name__ == "__main__":
    uv.run("main:app", host="127.0.0.1", port=8000, reload=True)