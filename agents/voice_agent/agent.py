from google.adk.agents import Agent
from google.adk.tools import google_search
from dotenv import load_dotenv

load_dotenv()

root_agent = Agent(
   name="copilot_voice",
   model="gemini-2.5-flash-native-audio-preview-09-2025",
   description="A lightweight background assistant that listens to user voice commands and helps perform simple everyday tasks.",
   instruction="",
   tools=[google_search],
)
