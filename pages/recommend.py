import re
import streamlit as st
from db import get_user, get_today_meals
from ai import get_recommendation
from utils import target_calories, sum_nutrients


def page_recommend(conn, model):
    st.markdown("""
        <div class="appbar">
          <div class="appbar-title">💡 맞춤 식단 추천</div>
          <div class="appbar-sub">신체 정보 기반 AI 추천</div>
        </div>""", unsafe_allow_html=True)

    if not st.session_state.uid:
        st.warning("👤 탭에서 내 정보를 먼저 입력해주세요.")
        return
    if not model:
        st.error("Gemini API 키를 설정해주세요.")
        return

    user  = get_user(conn, st.session_state.uid)
    meals = get_today_meals(conn, user["id"])
    tgt   = target_calories(user)
    n     = sum_nutrients(meals)
    remain = max(tgt - n["calories"], 0)

    st.markdown(f"""
        <div class="mini-grid" style="margin-bottom:12px">
          <div class="mini-card">
            <div class="mini-val" style="color:#ff7043">{n['calories']:.0f}</div>
            <div class="mini-label">오늘 섭취 kcal</div>
          </div>
          <div class="mini-card">
            <div class="mini-val" style="color:#27ae74">{remain:.0f}</div>
            <div class="mini-label">남은 여유 kcal</div>
          </div>
        </div>""", unsafe_allow_html=True)

    if st.button("🤖 AI 식단 추천 받기", use_container_width=True):
        with st.spinner("신체 정보 분석 중..."):
            st.session_state.rec_text = get_recommendation(model, user, meals)

    if st.session_state.rec_text:
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', st.session_state.rec_text)
        text = text.replace('\n', '<br>')
        st.markdown(f'<div class="rec-box">{text}</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="card" style="text-align:center;padding:32px 18px">
              <div style="font-size:2.5rem;margin-bottom:12px">🤖</div>
              <div style="color:#b08060;font-size:0.82rem">버튼을 누르면 인바디 &amp; 오늘 식사 기록을<br>분석해 맞춤 식단을 추천해드려요 🌿</div>
            </div>""", unsafe_allow_html=True)
