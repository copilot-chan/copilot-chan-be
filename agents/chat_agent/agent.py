import os
from dotenv import load_dotenv
import asyncio

from google.adk.agents import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import ToolContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.planners import BuiltInPlanner
from google.genai import types
from mem0 import AsyncMemoryClient

load_dotenv()

mem0 = AsyncMemoryClient()

# Define memory function tools
async def search_memory(query: str, tool_context: ToolContext) -> dict:
    """Searches the user's long-term memory for stored information.

    Args:
        query (str): The search query describing what information to retrieve (e.g., "user's current project", "user's interests").
    """
    user_id = tool_context.session.user_id
    filters = {"user_id": user_id}
    memories = await mem0.search(query, filters=filters)
    if memories.get('results', []):
        memory_list = memories['results']
        memory_context = "\n".join([f"{mem['id']} - {mem['memory']}" for mem in memory_list])
        return {"status": "success", "memories": memory_context}
    return {"status": "no_memories", "message": "No relevant memories found"}

async def delete_memory(memory_id: str) -> dict:
    """
    Delete a memory entry by ID.

    Args:
        memory_id (str): The memory entry ID to delete.
    """
    
    asyncio.create_task(mem0.delete(memory_id))
    return {"status": "success", "message": "Deleted"}

async def save_memory(content: str, tool_context: ToolContext) -> dict:
    """Saves important user-related information to long-term memory.

    Args:
        content (str): The information to be stored, such as user preferences, goals, projects, or settings.

    Returns:
        dict: A dictionary containing the operation result with a 'status' key ('success' or 'error').  
        If an error occurs, includes an 'error_message' key describing the issue.
    """
    user_id = tool_context.session.user_id
    
    try:
        asyncio.create_task(mem0.add([{"role": "user", "content": content}], user_id=user_id))
        return {"status": "success", "message": "Information saved to memory"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to save memory: {str(e)}"}

google_seacrh_agent = GoogleSearchTool(bypass_multi_tools_limit=True)

model_name = os.getenv("CHAT_MODEL_NAME", "gemini-2.5-flash")

tools = [
    google_seacrh_agent,
    search_memory,
    delete_memory,
    save_memory,
]

async def dynamic_instruction(context: ReadonlyContext) -> str:
    user_id = context.session.user_id
    filters = {"user_id": user_id}
    memories = await mem0.search("user_preferences", filters=filters)
    if memories.get("results"):
        lines = []
        for m in memories["results"]:
            lines.append(f"  - id: {m['id']}\n    content: \"{m['memory']}\"")
        memory_context = "<user_preferences>\nmemories:\n" + "\n".join(lines) + "\n</user_memory>"
    else:
        memory_context = "<user_preferences />"
    instruction = f"""
    Bạn là Copilot-chan — một trợ lý ảo thông minh và có trí nhớ.
    Bạn có thể lưu và truy xuất thông tin người dùng qua hai công cụ: search_memory và save_memory.

    Quy tắc:
    - Khi người dùng chia sẻ thông tin quan trọng (sở thích, thói quen, mục tiêu...), hãy lưu lại bằng save_memory.
    - Khi cần trả lời dựa trên kiến thức trước đây, hãy dùng search_memory để tìm lại.
    - Không nói cho người dùng biết bạn đang dùng tool; hãy thể hiện như bạn thực sự nhớ.
    - Giữ giọng điệu tự nhiên, gần gũi, nhưng chính xác và mạch lạc.
    - Khi thông tin thay đổi: use delete_memory(id) rồi save_memory(nội dung_mới). Đặc biệt là khi thấy thông tin từ người dùng sai khác với thông tin từ memory của bạn
    
    {memory_context}
    """.strip()

    return instruction

root_agent = Agent(
    name="copilot_chat",
    model=model_name,
    description="Trợ lý ảo có khả năng ghi nhớ và trò chuyện tự nhiên.",
    instruction=dynamic_instruction,
    tools=tools,
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=-1, # auto
        )    
    ),
)
