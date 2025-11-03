from dotenv import load_dotenv

from google import genai
from google.genai import types
from google.adk.events import Event

from core.utils.build_text_context import build_text_context

load_dotenv()

client = genai.Client()

system_instruction = """
Bạn nhận vào toàn bộ nội dung chat.
Nếu chủ đề không rõ hoặc chưa đủ thông tin → trả về đúng chữ "NO_TITLE".
Nếu chủ đề rõ → tạo một tiêu đề ngắn, 3–7 từ, súc tích.
Không giải thích. Không bình luận.
Có khả năng khi bắt đầu 1 cuộc trò chuyện người dùng sẽ chào hỏi chứ chưa vào chủ đề chính. Nếu chủ đề chưa rõ ràng thì trả về NO_TITLE
""".strip()

async def generate_title(query: str):
    response = await client.aio.models.generate_content(
        model = "gemini-flash-latest",
        contents=query,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )
    
    return response.text

async def generate_title_from_event(events: list[Event]):
    text_content = build_text_context(events=events)
    
    title = await generate_title(text_content)
    
    return title