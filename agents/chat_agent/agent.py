from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import google_search

load_dotenv()

root_agent = Agent(
   name="copilot_chat",
   model="gemini-2.5-flash-lite-preview-09-2025",
   description="",
   instruction="",
   tools=[google_search],
)

