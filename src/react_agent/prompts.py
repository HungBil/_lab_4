"""System prompt cho TravelBuddy agent."""

from pathlib import Path

# Đọc system prompt từ file system_prompt.txt ở root project
_PROMPT_FILE = Path(__file__).parent.parent.parent / "system_prompt.txt"

if _PROMPT_FILE.exists():
    SYSTEM_PROMPT = _PROMPT_FILE.read_text(encoding="utf-8")
else:
    # Fallback nếu file không tồn tại
    SYSTEM_PROMPT = "Bạn là TravelBuddy — trợ lý tư vấn du lịch nội địa Việt Nam. Luôn trả lời tiếng Việt."
