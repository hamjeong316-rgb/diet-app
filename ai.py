import json
import os
import streamlit as st
from datetime import datetime


@st.cache_resource
def get_model():
    import google.generativeai as genai
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except (FileNotFoundError, KeyError):
        key = os.getenv("GEMINI_API_KEY", "")
    if not key:
        return None
    genai.configure(api_key=key)
    return genai.GenerativeModel("gemini-3.1-flash-lite")
 
 
def _strip_json(text: str) -> str:
    text = text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return text.strip()
 

def analyze_image(model, img, user: dict) -> dict:
    prompt = f"""당신은 전문 영양사 AI입니다.

[사용자]
나이:{user.get('age')}세 성별:{user.get('gender')} 키:{user.get('height')}cm 체중:{user.get('weight')}kg
체지방:{user.get('body_fat_pct')}% 골격근:{user.get('muscle_mass')}kg
BMR:{user.get('bmr')}kcal TDEE:{user.get('tdee')}kcal
목표:{user.get('goal_weight')}kg ({user.get('goal_days')}일)

사진 속 음식만 분석해 반드시 아래 JSON만 응답(마크다운 없이). 사진에 보이는 시계, 날짜, 화면 등 시각 정보는 무시하세요:
{{
  "meal_type": "아침"|"점심"|"저녁"|"간식",
  "foods": [{{"name":"음식명","amount":"양","calories":숫자}}],
  "total_calories": 숫자,
  "carbs_g": 숫자,
  "protein_g": 숫자,
  "fat_g": 숫자,
  "carb_types": ["백미","국수" 등],
  "notes": "코멘트"
}}"""
    try:
        r = model.generate_content([prompt, img])
        return json.loads(_strip_json(r.text))
    except Exception as e:
        return {"error": str(e)}


def analyze_text(model, food_name: str, amount: str, meal_type: str, date_str: str, time_str: str) -> dict:
    prompt = f"""당신은 전문 영양사 AI입니다.
다음 텍스트를 바탕으로 영양소를 추정해 반드시 아래 JSON 포맷으로만 응답하세요(마크다운 제외).

[입력 정보]
음식: {food_name}
양: {amount}

{{
  "total_calories": 숫자,
  "carbs_g": 숫자,
  "protein_g": 숫자,
  "fat_g": 숫자,
  "carb_types": ["종류"],
  "notes": "직접 입력 계산 완료"
}}"""
    try:
        text = model.generate_content(prompt).text
        parsed = json.loads(_strip_json(text))
        parsed["timestamp"] = f"{date_str} {time_str}"
        parsed["meal_type"] = meal_type
        parsed["foods"] = [{"name": food_name, "amount": amount, "calories": parsed.get("total_calories", 0)}]
        return parsed
    except Exception as e:
        return {"error": str(e)}


def get_recommendation(model, user: dict, meals: list) -> str:
    from utils import sum_nutrients, target_calories
    n      = sum_nutrients(meals)
    tdee   = user.get("tdee", 2000)
    diff   = user.get("weight", 70) - user.get("goal_weight", 65)
    days   = max(user.get("goal_days", 90), 1)
    deficit = min((diff / days) * 7, 0.5) * 7700 / 7 if diff > 0 else 0
    target  = max(tdee - deficit, user.get("bmr", 1500) * 1.1)
    remain  = target - n["calories"]
    last_t  = meals[-1].get("meal_time") if meals else None
    if isinstance(last_t, str):
        last_t = datetime.fromisoformat(last_t)

    prompt = f"""전문 영양사 AI. 신체 맞춤 다음 식사 추천.
사용자: {user.get('weight')}kg→{user.get('goal_weight')}kg ({days}일)
BMR:{user.get('bmr'):.0f} TDEE:{tdee:.0f} 오늘목표:{target:.0f}kcal
오늘섭취: {n['calories']:.0f}kcal (탄{n['carbs']:.0f}g 단{n['protein']:.0f}g 지{n['fat']:.0f}g)
남은여유: {remain:.0f}kcal
마지막식사: {last_t.strftime('%H:%M') if last_t else '없음'}
현재시간: {datetime.now().strftime('%H:%M')}

한국어로 간결하게 응답:
1. 다음 식사 권장 시간 & 이유
2. 추천 메뉴 2가지 (각각 칼로리/탄수화물g/단백질g/지방g 명시)
3. 탄수화물 종류 권장 (복합당 위주 or 단순당 주의)
4. 오늘 한줄 조언"""
    try:
        return model.generate_content(prompt).text
    except Exception as e:
        return f"오류: {e}"