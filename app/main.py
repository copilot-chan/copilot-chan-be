from pathlib import Path

from fastapi import APIRouter
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.sessions import DatabaseSessionService
from google.adk.cli.fast_api import get_fast_api_app

from agents.chat_agent.agent import root_agent as chat_agent
from app.config import settings
from app.utils.user_id_extractor import user_id_extractor

BASE_DIR = Path(__file__).resolve().parent.parent
AGENTS_DIR = BASE_DIR / "agents"

app = get_fast_api_app(
    agents_dir=str(AGENTS_DIR),
    session_service_uri=settings.DB_URL,
    web=settings.IS_DEV,
)

session_service = DatabaseSessionService(db_url=settings.DB_URL)

adk_chat_agent = ADKAgent(
    adk_agent=chat_agent,
    app_name=settings.APP_NAME,
    user_id_extractor=user_id_extractor,
    session_timeout_seconds=3600,
    session_service=session_service
)

ag_ui_router = APIRouter(prefix="/ag-ui", tags=["AG-UI"])

add_adk_fastapi_endpoint(app=ag_ui_router, agent=adk_chat_agent, path="/chat")

app.include_router(ag_ui_router)

# Chạy bằng lệnh
# uvicorn app.main:app --reload