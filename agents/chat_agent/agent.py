from dotenv import load_dotenv
import asyncio

from google.adk.agents import Agent
from google.adk.tools.google_search_tool import GoogleSearchTool
from google.adk.tools import ToolContext
from google.adk.tools.load_web_page import load_web_page
from google.adk.agents.callback_context import CallbackContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.planners import BuiltInPlanner
from google.genai import types
from core.memory.client import mem0
from core.utils.generate_title import generate_title_from_event

load_dotenv()

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
        asyncio.create_task(mem0.add(content, user_id=user_id, infer=False))
        return {"status": "success", "message": "Information saved to memory"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to save memory: {str(e)}"}

google_seacrh_agent = GoogleSearchTool(bypass_multi_tools_limit=True)

tools = [
    google_seacrh_agent,
    search_memory,
    save_memory,
    load_web_page,
]

async def dynamic_instruction(context: ReadonlyContext) -> str:
    user_id = context.session.user_id
    filters = {"user_id": user_id}
    memories = await mem0.search("user_preferences", filters=filters)
    if memories.get("results"):
        memory_list = memories['results']
        memory_context = "\n".join([f"- {mem['memory']}" for mem in memory_list])
    else:
        memory_context = ""
    instruction = f"""
    Bạn là Copilot-chan — một trợ lý ảo thông minh và có trí nhớ.
    Bạn có thể lưu và truy xuất thông tin người dùng qua hai công cụ: search_memory và save_memory.

    Quy tắc:
    - Khi người dùng chia sẻ thông tin quan trọng (sở thích, thói quen, mục tiêu...), hãy lưu lại bằng save_memory. Những thông tin mà bạn nghĩ sẽ cần cho tương lai thì hãy lưu lại.
    - Khi cần trả lời dựa trên kiến thức trước đây, hãy dùng search_memory để tìm lại.
    - Khi gặp vấn đề mà bạn thiếu thông tin từ người dùng thì thử search_memory để tìm về thông tin đó.
    - Không nói cho người dùng biết bạn đang dùng tool; hãy thể hiện như bạn thực sự nhớ.
    - Giữ giọng điệu tự nhiên, gần gũi, nhưng chính xác và mạch lạc.
    - Chỉ gọi tool google_search_agent khi mà thông tin đó bạn thực sự không biết hoặc người dùng muốn lấy thông tin mới nhất từ internet
    
    <user_preferences>
    {memory_context}
    </user_preferences>
    """.strip()

    return instruction

async def after_agent_callback(callback_context: CallbackContext) -> types.Content | None:
    current_state = callback_context.state
    
    if current_state.get("title"):
        return
    
    title = await generate_title_from_event(callback_context.session.events)
    if not title == "NO_TITLE":
        current_state["title"] = title

reasoner_agent = Agent(
    name="ReasonerAgent",
    description="Xử lý các yêu cầu phức tạp như suy luận, giải toán và lập trình. Trước khi kích hoạt agent này, hãy báo cho người dùng theo kiểu: 'Để tôi suy nghĩ kỹ hơn một chút...'.",
    model="gemini-2.5-pro",
    planner=BuiltInPlanner(
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=-1, # auto
        )
    ),
    tools=tools,
    instruction=dynamic_instruction,
    after_agent_callback=after_agent_callback,
)

root_agent = Agent(
    name="RootAgent",
    model="gemini-flash-latest",
    description="Trợ lý ảo có khả năng ghi nhớ và trò chuyện tự nhiên.",
    instruction=dynamic_instruction,
    tools=tools,
    after_agent_callback=after_agent_callback,
    sub_agents=[reasoner_agent]
)
