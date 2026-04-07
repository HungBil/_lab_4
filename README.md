# TravelBuddy — ReAct Agent Tư Vấn Du Lịch Việt Nam

Trợ lý tư vấn du lịch nội địa Việt Nam sử dụng **LangGraph** + **OpenRouter** (GPT-4o-mini).

## Tính năng

- 🔍 **Tìm chuyến bay** nội địa (mock data)
- 🏨 **Tìm khách sạn** theo thành phố, lọc theo giá
- 💰 **Tính ngân sách** chuyến đi
- 🔗 **Multi-step tool chaining** — tự động gọi 3 tools khi đủ thông tin
- 🛡️ **Guardrails** — từ chối ngoài phạm vi, hỏi lại khi thiếu thông tin

## Cấu trúc project

```
├── system_prompt.txt   # System prompt cho agent
├── tools.py            # 3 tools: search_flights, search_hotels, calculate_budget
├── agent.py            # LangGraph ReAct agent + CLI
├── test_results.md     # Kết quả test 5 test cases
├── run_tests.py        # Script test tự động
├── .env.example        # Template file môi trường
└── requirements.txt    # Dependencies
```

## Cài đặt và chạy

### 1. Clone repo

```bash
git clone <repo-url>
cd <repo-name>
```

### 2. Cài dependencies

```bash
pip install -r requirements.txt
```

### 3. Tạo file `.env`

```bash
cp .env.example .env
```

Mở `.env` và paste API key của bạn:

```
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

> Lấy key tại [https://openrouter.ai/keys](https://openrouter.ai/keys)

### 4. Chạy agent

```bash
python agent.py
```

### 5. Chạy test tự động

```bash
python run_tests.py
```

## Kết quả test

| Test | Mô tả | Kết quả |
|------|--------|---------|
| Test 1 | Chào hỏi chung | ✅ PASS |
| Test 2 | Tìm chuyến bay HN→ĐN | ✅ PASS |
| Test 3 | Multi-step Phú Quốc 2 đêm 5 triệu | ✅ PASS |
| Test 4 | Clarification (thiếu info) | ✅ PASS |
| Test 5 | Refusal (ngoài scope) | ✅ PASS |

Chi tiết xem [test_results.md](./test_results.md).

## Kiến trúc agent

```
START → agent_node → should_continue? ─── có tool_calls → ToolNode → agent_node (loop)
                                       └── không         → END
```

- **agent_node**: Gọi LLM với system prompt, trả về response
- **ToolNode**: Thực thi tools được gọi (search_flights, search_hotels, calculate_budget)
- **should_continue**: Kiểm tra response có tool_calls không → routing

## Tools (Mock Data)

| Tool | Mô tả | Tuyến/Thành phố có sẵn |
|------|--------|------------------------|
| `search_flights(origin, destination)` | Tìm chuyến bay | HN↔ĐN, HN↔PQ, HN↔HCM, HCM↔ĐN, HCM↔PQ |
| `search_hotels(city, max_price_per_night)` | Tìm khách sạn | Đà Nẵng, Phú Quốc, Hồ Chí Minh |
| `calculate_budget(total_budget, expenses)` | Tính ngân sách | Format: "tên:số_tiền,tên:số_tiền" |
