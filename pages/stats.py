import json
import streamlit as st
from datetime import date
from itertools import groupby
from db import get_meals_by_date


def page_stats(conn):
    st.markdown("""
        <div class="appbar">
          <div class="appbar-title">📅 날짜별 상세 기록</div>
        </div>""", unsafe_allow_html=True)

    if not st.session_state.uid:
        return

    selected_date = st.date_input("날짜 선택", value=date.today())
    meals = get_meals_by_date(conn, st.session_state.uid, selected_date.isoformat())

    if not meals:
        st.markdown(
            '<div class="card" style="text-align:center;padding:32px;color:#b08060">기록이 없습니다 📭</div>',
            unsafe_allow_html=True,
        )
        return

    for time_key, group in groupby(meals, key=lambda x: x["meal_time"][11:16]):
        group_list = list(group)
        total_cal  = sum(m["total_calories"] for m in group_list)

        food_pairs = []
        for m in group_list:
            items = json.loads(m["food_items"]) if isinstance(m["food_items"], str) else m["food_items"]
            for f in items:
                if isinstance(f, dict):
                    food_pairs.append(f"{f['name']} {f['amount']}")

        st.markdown(f"""
            <div class="card">
              <div style="display:flex;justify-content:space-between;margin-bottom:8px">
                <span style="font-weight:800;color:#ff7043">{time_key}</span>
                <span style="color:#3d2c1e;font-weight:700">{total_cal} kcal</span>
              </div>
              <div style="color:#7a5c47;font-size:0.9rem">{", ".join(food_pairs)}</div>
            </div>""", unsafe_allow_html=True)
