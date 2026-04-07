"""Test tự động 5 test case — chạy agent thật qua OpenRouter."""

import logging
import os
import sys

from dotenv import load_dotenv

# Thêm src/ vào path (file ở tests/, cần lên 1 cấp về project root)
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_PROJECT_ROOT, "src"))

# Load .env từ project root
os.chdir(_PROJECT_ROOT)

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

from langchain_core.messages import AIMessage  # noqa: E402
from react_agent.graph import graph  # noqa: E402

# ---------------------------------------------------------------------------
# 5 Test Cases
# ---------------------------------------------------------------------------

TEST_CASES = [
    {
        "name": "Test 1: Chào hỏi chung",
        "input": "Xin chào! Tôi đang muốn đi du lịch nhưng chưa biết đi đâu.",
        "expect_tools": False,
        "expect_description": "Chào lại + hỏi sở thích/ngân sách, không gọi tool",
    },
    {
        "name": "Test 2: Tìm chuyến bay",
        "input": "Tìm giúp tôi chuyến bay từ Hà Nội đi Đà Nẵng",
        "expect_tools": True,
        "expect_description": "Gọi search_flights, liệt kê 4 chuyến bay",
    },
    {
        "name": "Test 3: Multi-step (Phú Quốc 2 đêm 5 triệu)",
        "input": "Tôi ở Hà Nội, muốn đi Phú Quốc 2 đêm, budget 5 triệu. Tư vấn giúp!",
        "expect_tools": True,
        "expect_description": "Gọi search_flights + search_hotels + calculate_budget",
    },
    {
        "name": "Test 4: Clarification",
        "input": "Tôi muốn đặt khách sạn",
        "expect_tools": False,
        "expect_description": "Hỏi lại thành phố/ngân sách, không gọi tool",
    },
    {
        "name": "Test 5: Refusal",
        "input": "Giải giúp tôi bài tập lập trình Python về linked list",
        "expect_tools": False,
        "expect_description": "Từ chối lịch sự, chỉ hỗ trợ du lịch",
    },
]


def extract_tool_calls(messages: list) -> list[str]:
    """Lấy danh sách tool names từ messages."""
    tool_names = []
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                tool_names.append(tc["name"])
    return tool_names


def run_test(test: dict) -> dict:
    """Chạy 1 test case."""
    print(f"\n{'=' * 60}")
    print(f"  {test['name']}")
    print(f"  Input: \"{test['input']}\"")
    print(f"  Expect: {test['expect_description']}")
    print(f"{'=' * 60}")

    try:
        result = graph.invoke({"messages": [{"role": "user", "content": test["input"]}]})
        messages = result["messages"]

        tool_names = extract_tool_calls(messages)

        final_answer = ""
        for msg in reversed(messages):
            if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                final_answer = msg.content
                break

        has_tools = len(tool_names) > 0
        tools_match = has_tools == test["expect_tools"]

        print(f"\n  Tool calls: {tool_names if tool_names else 'Không'}")
        print(f"  Tools expected: {'Có' if test['expect_tools'] else 'Không'} | Actual: {'Có' if has_tools else 'Không'} | {'✅' if tools_match else '❌'}")
        print(f"\n  Final answer:\n  {final_answer[:500]}")

        status = "✅ PASS" if tools_match else "❌ FAIL"
        print(f"\n  → {status}")

        return {"name": test["name"], "tool_calls": tool_names, "pass": tools_match}

    except Exception as e:
        print(f"\n  ❌ ERROR: {e}")
        return {"name": test["name"], "tool_calls": [], "pass": False}


def main():
    """Chạy 5 test cases."""
    print("🌴 TravelBuddy — Chạy 5 test case tự động")
    print("=" * 60)

    results = []
    for test in TEST_CASES:
        results.append(run_test(test))

    print(f"\n\n{'=' * 60}")
    print("  TỔNG KẾT")
    print(f"{'=' * 60}")
    passed = sum(1 for r in results if r["pass"])
    for r in results:
        status = "✅" if r["pass"] else "❌"
        tools_str = ", ".join(r["tool_calls"]) if r["tool_calls"] else "Không"
        print(f"  {status} {r['name']} | Tools: {tools_str}")

    print(f"\n  Kết quả: {passed}/{len(results)} PASS")


if __name__ == "__main__":
    main()
