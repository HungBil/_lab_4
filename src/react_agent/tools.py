"""Travel agent tools: search_flights, search_hotels, calculate_budget.

Sử dụng mock data — không gọi API bên ngoài.
"""

from langchain_core.tools import tool

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def format_vnd(amount: int) -> str:
    """Format số tiền theo kiểu Việt Nam: 1.450.000đ."""
    return f"{amount:,.0f}đ".replace(",", ".")


# ---------------------------------------------------------------------------
# Mock Data
# ---------------------------------------------------------------------------

FLIGHTS_DB: dict = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1450000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2800000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1200000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2100000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1350000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1100000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1600000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1300000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3200000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1300000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1100000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650000, "class": "economy"},
    ],
}

HOTELS_DB: dict = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1800000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1200000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3500000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1500000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2800000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1400000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180000, "area": "Quận 1", "rating": 4.6},
    ],
}


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def search_flights(origin: str, destination: str) -> str:
    """Tìm chuyến bay nội địa Việt Nam.

    Args:
        origin: Thành phố khởi hành (ví dụ: Hà Nội, Hồ Chí Minh).
        destination: Thành phố đến (ví dụ: Đà Nẵng, Phú Quốc).
    """
    flights = FLIGHTS_DB.get((origin, destination))

    # Thử chiều ngược nếu không tìm thấy
    if flights is None:
        flights = FLIGHTS_DB.get((destination, origin))
        if flights is not None:
            origin, destination = destination, origin

    if not flights:
        return f"Không tìm thấy chuyến bay từ {origin} đến {destination}. Các tuyến có sẵn: " + \
               ", ".join(f"{o} → {d}" for o, d in FLIGHTS_DB.keys())

    lines: list[str] = [f"✈️ Chuyến bay từ {origin} → {destination} ({len(flights)} kết quả):\n"]
    for i, f in enumerate(flights, 1):
        lines.append(
            f"  {i}. {f['airline']} | {f['departure']}→{f['arrival']} | "
            f"{format_vnd(f['price'])} | Hạng: {f['class']}"
        )
    return "\n".join(lines)


@tool
def search_hotels(city: str, max_price_per_night: int = 99_999_999) -> str:
    """Tìm khách sạn tại thành phố du lịch Việt Nam.

    Args:
        city: Tên thành phố (ví dụ: Đà Nẵng, Phú Quốc, Hồ Chí Minh).
        max_price_per_night: Giá tối đa mỗi đêm (VNĐ). Mặc định không giới hạn.
    """
    hotels = HOTELS_DB.get(city)

    if hotels is None:
        return f"Không có dữ liệu khách sạn tại {city}. Các thành phố có sẵn: " + \
               ", ".join(HOTELS_DB.keys())

    filtered = [h for h in hotels if h["price_per_night"] <= max_price_per_night]

    if not filtered:
        return (
            f"Không tìm thấy khách sạn tại {city} với giá ≤ {format_vnd(max_price_per_night)}/đêm. "
            f"Giá thấp nhất hiện có: {format_vnd(min(h['price_per_night'] for h in hotels))}/đêm."
        )

    filtered.sort(key=lambda h: (-h["rating"], h["price_per_night"]))

    lines: list[str] = [f"🏨 Khách sạn tại {city} (giá ≤ {format_vnd(max_price_per_night)}/đêm, {len(filtered)} kết quả):\n"]
    for i, h in enumerate(filtered, 1):
        stars = "⭐" * h["stars"]
        lines.append(
            f"  {i}. {h['name']} {stars}\n"
            f"     Giá: {format_vnd(h['price_per_night'])}/đêm | Khu vực: {h['area']} | Rating: {h['rating']}"
        )
    return "\n".join(lines)


@tool
def calculate_budget(total_budget: int, expenses: str) -> str:
    """Tính toán ngân sách chuyến đi.

    Args:
        total_budget: Tổng ngân sách (VNĐ), ví dụ 5000000.
        expenses: Chuỗi chi phí, format "tên_mục:số_tiền,tên_mục:số_tiền".
                  Ví dụ: "vé_bay:1100000,khách_sạn:1600000,ăn_uống:600000"
    """
    items: list[tuple[str, int]] = []
    total_expense = 0

    try:
        for part in expenses.split(","):
            part = part.strip()
            if not part:
                continue
            name, value_str = part.split(":")
            value = int(value_str.strip())
            items.append((name.strip(), value))
            total_expense += value
    except (ValueError, TypeError):
        return (
            f"Lỗi: Không thể parse chuỗi chi phí. "
            f"Format đúng: \"tên_mục:số_tiền,tên_mục:số_tiền\"\n"
            f"Ví dụ: \"vé_bay:1100000,khách_sạn:1600000\"\n"
            f"Chuỗi nhận được: \"{expenses}\""
        )

    remaining = total_budget - total_expense

    lines: list[str] = [
        "💰 BẢNG NGÂN SÁCH CHUYẾN ĐI\n",
        f"  Tổng ngân sách: {format_vnd(total_budget)}\n",
        "  Chi tiết chi phí:",
    ]
    for name, value in items:
        label = name.replace("_", " ").capitalize()
        lines.append(f"    • {label}: {format_vnd(value)}")

    lines.append(f"\n  Tổng chi: {format_vnd(total_expense)}")
    lines.append(f"  Còn lại:  {format_vnd(remaining)}")

    if remaining < 0:
        lines.append(f"\n  ⚠️ CẢNH BÁO: Vượt ngân sách {format_vnd(abs(remaining))}!")
    elif remaining > 0:
        lines.append(f"\n  ✅ Còn dư {format_vnd(remaining)} cho chi phí phát sinh.")

    return "\n".join(lines)


# Export tools list
TOOLS = [search_flights, search_hotels, calculate_budget]
