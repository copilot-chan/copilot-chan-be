from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint

from agents.chat_agent.agent import root_agent as chat_agent
from app.config import settings
from app.utils.user_id_extractor import user_id_extractor

app = FastAPI(title="Copilot Chan Backend")

adk_chat_agent = ADKAgent(
    adk_agent=chat_agent,
    app_name=settings.APP_NAME,
    user_id_extractor=user_id_extractor,
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

add_adk_fastapi_endpoint(app=app, agent=adk_chat_agent, path="/api/chat")

# Chạy bằng lệnh
# uvicorn app.main:app --reload