"""TravelBuddy — CLI entry point.

Chạy: python agent.py
"""

import logging
import os
import sys

from dotenv import load_dotenv

# Thêm src/ vào path để import react_agent package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
# Tắt log HTTP request của httpx/openai
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

from langchain_core.messages import AIMessage  # noqa: E402
from react_agent.graph import graph  # noqa: E402


def main() -> None:
    """Chạy chatbot trong terminal."""
    print("=" * 50)
    print("  🌴 TravelBuddy — Trợ lý du lịch Việt Nam")
    print("  Gõ 'quit', 'exit' hoặc 'q' để thoát.")
    print("=" * 50)

    messages: list = []

    while True:
        try:
            user_input = input("\n🧑 Bạn: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Tạm biệt!")
            break

        if user_input.lower() in ("quit", "exit", "q", ""):
            print("👋 Tạm biệt! Chúc bạn có chuyến du lịch vui vẻ!")
            break

        messages.append({"role": "user", "content": user_input})

        result = graph.invoke({"messages": messages})
        messages = result["messages"]

        # In câu trả lời cuối cùng
        last_msg = result["messages"][-1]
        print(f"\n🤖 TravelBuddy: {last_msg.content}")


if __name__ == "__main__":
    main()
