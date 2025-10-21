from google.adk.agents import Agent
from google.adk.tools import google_search
from fastapi import FastAPI
from ag_ui_adk import ADKAgent, add_adk_fastapi_endpoint
from dotenv import load_dotenv

load_dotenv()

root_agent = Agent(
   name="copilot_chat",
   model="gemini-2.5-flash-lite-preview-09-2025",
   description="",
   instruction="",
   tools=[google_search],
)

# Create ADK middleware agent instance
adk_agent_sample = ADKAgent(
    adk_agent=root_agent,
    app_name="demo_app",
    user_id="demo_user",
    session_timeout_seconds=3600,
    use_in_memory_services=True
)

# Create FastAPI app
app = FastAPI(title="ADK Middleware Sample Agent")

# Add the ADK endpoint
add_adk_fastapi_endpoint(app, adk_agent_sample, path="/")

# If you want the server to run on invocation, you can do the following:
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
