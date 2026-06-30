import os
import streamlit as st
from supabase import create_client, Client
import json
from datetime import date
from dotenv import load_dotenv

load_dotenv()

@st.cache_resource
def get_db():
    url = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    key = st.secrets.get("SUPABASE_KEY") or os.getenv("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Supabase URL 또는 Key를 찾을 수 없습니다.")
        
    # 양끝 공백(\n, 스페이스) 및 따옴표 제거 (클라우드 파싱 에러 방지)
    url = url.strip().strip('"').strip("'")
    key = key.strip().strip('"').strip("'")
    
    return create_client(url, key)


def save_user(conn, d):
    data = {
        "name": d["name"], "age": d["age"], "gender": d["gender"],
        "height": d["height"], "weight": d["weight"],
        "body_fat_pct": d["body_fat_pct"], "muscle_mass": d["muscle_mass"],
        "bmr": d["bmr"], "tdee": d["tdee"],
        "visceral_fat": d.get("visceral_fat"),
        "body_fat_mass": d.get("body_fat_mass"),
        "goal_weight": d["goal_weight"],
        "goal_days": d["goal_days"],
        "goal_start_date": d["goal_start_date"],
    }
    if d.get("password"):
        data["password"] = d["password"]
    try:
        if d.get("id"):
            conn.table("UserMaster").update(data).eq("id", d["id"]).execute()
            return d["id"]
        else:
            res = conn.table("UserMaster").insert(data).execute()
            return res.data[0]["id"]
    except Exception as e:
        st.error(f"사용자 저장 오류: {e}")
        return None


def get_user(conn, uid):
    try:
        res = conn.table("UserMaster").select("*").eq("id", uid).single().execute()
        return res.data
    except:
        return None


def get_all_users(conn):
    try:
        res = conn.table("UserMaster").select("id, name, password").order("id").execute()
        return res.data
    except Exception as e:
        st.error(f"사용자 목록 조회 오류: {e}")
        return []


def save_meal(conn, m):
    data = {
        "user_id":        m["user_id"],
        "meal_time":      m["meal_time"],
        "meal_type":      m["meal_type"],
        "food_items":     json.dumps(m["food_items"], ensure_ascii=False),
        "total_calories": m["total_calories"],
        "carbs_g":        m["carbs_g"],
        "protein_g":      m["protein_g"],
        "fat_g":          m["fat_g"],
        "carb_types":     json.dumps(m.get("carb_types", []), ensure_ascii=False),
        "raw_analysis":   m.get("raw_analysis", ""),
    }
    try:
        conn.table("DailyMealRecord").insert(data).execute()
        return True
    except Exception as e:
        st.error(f"식사 저장 오류: {e}")
        return None


def get_today_meals(conn, uid):
    today = date.today().isoformat()
    try:
        res = (
            conn.table("DailyMealRecord")
            .select("*")
            .eq("user_id", uid)
            .gte("meal_time", f"{today}T00:00:00")
            .lte("meal_time", f"{today}T23:59:59")
            .order("meal_time")
            .execute()
        )
        out = []
        for r in res.data:
            out.append({
                "meal_time":      r["meal_time"],
                "meal_type":      r["meal_type"],
                "food_items":     json.loads(r["food_items"]) if r["food_items"] else [],
                "total_calories": r["total_calories"],
                "carbs_g":        r["carbs_g"],
                "protein_g":      r["protein_g"],
                "fat_g":          r["fat_g"],
                "carb_types":     json.loads(r["carb_types"]) if r["carb_types"] else [],
            })
        return out
    except Exception as e:
        st.error(f"식사 조회 오류: {e}")
        return []


def get_meals_by_date(conn, uid, target_date_str):
    try:
        res = (
            conn.table("DailyMealRecord")
            .select("*")
            .eq("user_id", uid)
            .gte("meal_time", f"{target_date_str}T00:00:00")
            .lte("meal_time", f"{target_date_str}T23:59:59")
            .order("meal_time")
            .execute()
        )
        return res.data
    except Exception as e:
        st.error(f"조회 오류: {e}")
        return []


def get_monthly_meals(conn, uid, year, month):
    import calendar
    start_date = f"{year}-{month:02d}-01"
    last_day   = calendar.monthrange(year, month)[1]
    end_date   = f"{year}-{month:02d}-{last_day}"
    try:
        res = (
            conn.table("DailyMealRecord")
            .select("*")
            .eq("user_id", uid)
            .gte("meal_time", f"{start_date}T00:00:00")
            .lte("meal_time", f"{end_date}T23:59:59")
            .order("meal_time")
            .execute()
        )
        return res.data
    except Exception as e:
        st.error(f"월별 조회 오류: {e}")
        return []