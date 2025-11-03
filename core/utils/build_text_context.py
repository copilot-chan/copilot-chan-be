from google.adk.events import Event

def build_text_context(events: list[Event], max_chars: int = 2000) -> str:
    """Trả về context dạng text để feed vào LLM tạo tiêu đề."""
    lines = []
    for ev in events:
        if ev.content and ev.content.parts:
            for part in ev.content.parts:
                if part.text and not part.thought:
                    text = part.text.strip()
                    if text:
                        lines.append(f"{ev.content.role}: {text}")

    context = "\n".join(lines)

    # cắt bớt nếu quá dài (tạo tiêu đề không cần full)
    if len(context) > max_chars:
        context = context[-max_chars:]  # lấy phần cuối gần nhất cuộc hội thoại
    return context