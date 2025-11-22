import io

import httpx
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from google.adk.sessions import DatabaseSessionService

from agents.chat_agent.agent import root_agent as chat_agent
from app.config import settings
from app.utils.user_id_extractor import user_id_extractor
from app.deps import get_current_uid
from app.routers.memory import router as memory_router

app = FastAPI()

session_service = DatabaseSessionService(
    db_url=settings.DB_URL,
    connect_args={
        "ssl": True,
        # "channel_binding": "require"
    }
)

adk_chat_agent = ADKAgent(
    adk_agent=chat_agent,
    app_name=settings.APP_NAME,
    user_id_extractor=user_id_extractor,
    session_timeout_seconds=3600,
    session_service=session_service,
    cleanup_interval_seconds=float("inf"),
)

ag_ui_router = APIRouter(prefix="/ag-ui", tags=["AG-UI"])

add_adk_fastapi_endpoint(app=ag_ui_router, agent=adk_chat_agent, path="/chat")

app.include_router(ag_ui_router)
app.include_router(memory_router)

@app.api_route("/apps/{app_name}/users/{user_id}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_user_apps(
    app_name: str,
    user_id: str,
    path: str,
    request: Request,
    uid: str = Depends(get_current_uid)
):
    """
    Proxy all endpoints /apps/{app_name}/users/{user_id}/... to the backend
    and validate that uid matches user_id.
    """
    # Validate uid
    if uid != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Create the full backend URL
    url = f"http://127.0.0.1:{settings.LOCAL_AGENT_PORT}/apps/{app_name}/users/{user_id}/{path}"

    # Get the original method and body
    method = request.method
    body = await request.body()

    # Copy headers from the client
    headers = dict(request.headers)
    headers.pop("host", None)

    async with httpx.AsyncClient(follow_redirects=False) as client:
        try:
            resp = await client.request(
                method=method,
                url=url,
                content=body,
                headers=headers,
                timeout=30.0
            )
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Filter out headers that should not be copied
    excluded_headers = ["content-length", "transfer-encoding", "connection", "keep-alive"]
    proxy_headers = {k: v for k, v in resp.headers.items() if k.lower() not in excluded_headers}

    # Return StreamingResponse to keep the response as is
    return StreamingResponse(
        io.BytesIO(resp.content),
        status_code=resp.status_code,
        headers=proxy_headers,
        media_type=resp.headers.get("content-type")
    )
