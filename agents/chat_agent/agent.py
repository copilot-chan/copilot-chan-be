from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools import ToolContext
from mem0 import AsyncMemoryClient

load_dotenv()

mem0 = AsyncMemoryClient()

# Define memory function tools
async def search_memory(query: str, tool_context: ToolContext) -> dict:
    """Searches the user's long-term memory for stored information.

    Args:
        query (str): The search query describing what information to retrieve (e.g., "user's current project", "user's interests").

    Returns:
        dict: A dictionary containing search results with a 'status' key ('success' or 'no_memories').  
        If successful, includes a 'results' key with the retrieved memory entries.
    """
    user_id = tool_context.session.user_id
    filters = {"user_id": user_id}
    memories = await mem0.search(query, filters=filters)
    if memories.get('results', []):
        memory_list = memories['results']
        memory_context = "\n".join([f"- {mem['memory']}" for mem in memory_list])
        return {"status": "success", "memories": memory_context}
    return {"status": "no_memories", "message": "No relevant memories found"}

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
        mem0.add([{"role": "user", "content": content}], user_id=user_id)
        return {"status": "success", "message": "Information saved to memory"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to save memory: {str(e)}"}

tools = [
    google_search,
    search_memory,
    save_memory,
]

root_agent = Agent(
    name="copilot_chat",
    model="gemini-2.5-flash",
    description="Trợ lý ảo có khả năng ghi nhớ và trò chuyện tự nhiên.",
    instruction="""
    Bạn là Copilot-chan — một trợ lý ảo thông minh và có trí nhớ.
    Bạn có thể lưu và truy xuất thông tin người dùng qua hai công cụ: search_memory và save_memory.

    Quy tắc:
    - Khi người dùng chia sẻ thông tin quan trọng (sở thích, thói quen, mục tiêu...), hãy lưu lại bằng save_memory.
    - Khi cần trả lời dựa trên kiến thức trước đây, hãy dùng search_memory để tìm lại.
    - Không nói cho người dùng biết bạn đang dùng tool; hãy thể hiện như bạn thực sự nhớ.
    - Giữ giọng điệu tự nhiên, gần gũi, nhưng chính xác và mạch lạc.
    """,
    tools=tools,
)
