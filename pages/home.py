import streamlit as st
from datetime import datetime
from db import get_user, get_today_meals
from utils import target_calories, sum_nutrients, goal_progress, distinct_meal_count, parse_meal_time


def page_home(conn, logout_fn):
    user = get_user(conn, st.session_state.uid)
    now  = datetime.now()

    # ── 헤더 ──
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.markdown(f'<div class="appbar-title">🥗 {user.get("name","사용자")}님</div>', unsafe_allow_html=True)
    with c2:
        st.button(":material/cached: 전환", on_click=logout_fn, key="logout_btn", use_container_width=True)
    with c3:
        if st.button(":material/face: 정보", use_container_width=True):
            st.session_state.pg = "profile"
            st.rerun()
    st.markdown(f'<div class="appbar-sub">{now.strftime("%m월 %d일")} · {now.strftime("%H:%M")}</div>',
                unsafe_allow_html=True)

    if not user:
        st.markdown("""
            <div class="card" style="text-align:center;padding:32px 18px">
              <div style="font-size:2.5rem;margin-bottom:12px">👤</div>
              <div style="color:#3d2c1e;font-weight:700;margin-bottom:6px">내 정보를 먼저 입력해주세요</div>
              <div style="color:#b08060;font-size:0.82rem">하단 탭에서 인바디 &amp; 목표를 설정하면<br>맞춤 식단 관리가 시작됩니다</div>
            </div>""", unsafe_allow_html=True)
        return

    meals   = get_today_meals(conn, user["id"])
    tgt_cal = target_calories(user)
    n       = sum_nutrients(meals)
    cal_in  = n["calories"]
    remain  = max(tgt_cal - cal_in, 0)
    pct     = min(cal_in / tgt_cal * 100, 100) if tgt_cal > 0 else 0

    # ── 칼로리 카드 ──
    bar_color = "#f87171" if pct > 100 else "linear-gradient(90deg,#ff7043,#ffa270)"
    st.markdown(f"""
        <div class="card">
          <div class="card-title">오늘 섭취 칼로리</div>
          <div class="big-num">{cal_in:.0f}<span class="big-unit">kcal</span></div>
          <div style="margin:14px 0 6px">
            <div style="display:flex;justify-content:space-between;font-size:0.72rem;color:#b08060;margin-bottom:5px">
              <span>목표 {tgt_cal:.0f} kcal</span><span>남음 {remain:.0f} kcal</span>
            </div>
            <div class="bar-bg"><div class="bar-fill" style="width:{pct:.0f}%;background:{bar_color}"></div></div>
          </div>
        </div>""", unsafe_allow_html=True)

    # ── 영양소 바 카드 ──
    tgt_c = tgt_cal * 0.5 / 4
    tgt_p = tgt_cal * 0.25 / 4
    tgt_f = tgt_cal * 0.25 / 9
    nutrients = [
        ("탄수화물", "#ff7043", n["carbs"],   tgt_c),
        ("단백질",   "#27ae74", n["protein"], tgt_p),
        ("지방",     "#f472b6", n["fat"],     tgt_f),
    ]
    html = '<div class="card"><div class="card-title">영양소 달성</div>'
    for name, color, curr, tgt in nutrients:
        p = min(curr / tgt * 100, 100) if tgt > 0 else 0
        html += f"""
          <div class="nutr-row">
            <div class="nutr-top">
              <span class="nutr-name">{name}</span>
              <span class="nutr-val">{curr:.0f}g / {tgt:.0f}g</span>
            </div>
            <div class="bar-bg"><div class="bar-fill" style="width:{p:.0f}%;background:{color}"></div></div>
          </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # ── D-Day & 진행률 ──
    elapsed, dday, goal_days, prog = goal_progress(user)
    meal_count = distinct_meal_count(meals)

    st.markdown(f"""
        <div class="mini-grid">
          <div class="mini-card">
            <div class="mini-val">D-{dday}</div>
            <div class="mini-label">목표까지</div>
          </div>
          <div class="mini-card">
            <div class="mini-val">{meal_count}</div>
            <div class="mini-label">오늘 식사 횟수</div>
          </div>
        </div>
        <div class="card" style="margin-top:12px">
          <div class="card-title">다이어트 진행률</div>
          <div style="display:flex;justify-content:space-between;font-size:0.75rem;color:#b08060;margin-bottom:6px">
            <span>{user.get('weight')}kg → {user.get('goal_weight')}kg</span>
            <span>{elapsed}/{goal_days}일</span>
          </div>
          <div class="progress-bg"><div class="progress-fill" style="width:{prog:.0f}%"></div></div>
        </div>""", unsafe_allow_html=True)

    # ── 식사 타임라인 ──
    html = '<div class="card"><div class="card-title">오늘 식사 기록</div>'
    if not meals:
        html += '<p style="color:#b08060;font-size:0.82rem;text-align:center;padding:16px 0">📸 탭에서 식사를 기록해보세요 🍽️</p>'
    else:
        for i, m in enumerate(meals):
            tstr  = parse_meal_time(m.get("meal_time"))
            foods = m.get("food_items", [])
            fname = ", ".join(
                (f["name"] if isinstance(f, dict) else str(f)) for f in foods
            ) if foods else m.get("meal_type", "식사")
            line_html = "" if i == len(meals) - 1 else '<div class="meal-line"></div>'
            html += f"""
              <div class="meal-item">
                <span class="meal-time-label">{tstr}</span>
                <div class="meal-dot-wrap"><div class="meal-dot"></div>{line_html}</div>
                <div>
                  <div class="meal-name">{fname[:24]}</div>
                  <div class="meal-cal">{m.get("total_calories",0):.0f} kcal</div>
                  <div class="meal-macro">탄 {m.get("carbs_g",0):.0f}g · 단 {m.get("protein_g",0):.0f}g · 지 {m.get("fat_g",0):.0f}g</div>
                </div>
              </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)
