import hashlib
from datetime import datetime, date


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

ACT_FACTOR = {
    "거의 없음": 1.2,
    "약간":      1.375,
    "보통":      1.55,
    "활발함":    1.725,
    "매우 활발": 1.9,
}


def calc_bmr(gender: str, weight: float, height: float, age: int) -> float:
    base = 10 * weight + 6.25 * height - 5 * age
    return base + 5 if gender == "남성" else base - 161


def calc_tdee(bmr: float, act: str) -> float:
    return bmr * ACT_FACTOR.get(act, 1.55)


def target_calories(user: dict) -> float:
    tdee   = user.get("tdee", 2000)
    diff   = user.get("weight", 70) - user.get("goal_weight", 65)
    days   = max(user.get("goal_days", 90), 1)
    deficit = min((diff / days) * 7, 0.5) * 7700 / 7 if diff > 0 else 0
    return max(tdee - deficit, user.get("bmr", 1500) * 1.1)


def parse_meal_time(mt) -> str:
    """Return 'HH:MM' string from various meal_time formats."""
    if isinstance(mt, datetime):
        return mt.strftime("%H:%M")
    if isinstance(mt, str):
        cleaned = mt.replace("T", " ").strip()
        return cleaned[11:16] if len(cleaned) >= 16 else cleaned
    return "--"


def distinct_meal_count(meals: list) -> int:
    times = set()
    for m in meals:
        if m.get("meal_type") == "식사":
            times.add(parse_meal_time(m.get("meal_time")))
    return len(times)


def sum_nutrients(meals: list) -> dict:
    return {
        "calories": sum(m.get("total_calories", 0) for m in meals),
        "carbs":    sum(m.get("carbs_g",        0) for m in meals),
        "protein":  sum(m.get("protein_g",      0) for m in meals),
        "fat":      sum(m.get("fat_g",          0) for m in meals),
    }


def goal_progress(user: dict):
    start    = user.get("goal_start_date")
    goal_days = max(user.get("goal_days", 90), 1)
    if start:
        if isinstance(start, str):
            start = date.fromisoformat(start)
        elapsed = (date.today() - start).days
        dday    = max(goal_days - elapsed, 0)
    else:
        elapsed, dday = 0, goal_days
    pct = min(elapsed / goal_days * 100, 100)
    return elapsed, dday, goal_days, pct