import streamlit as st
from datetime import date
from db import get_user, save_user
from utils import calc_bmr, calc_tdee, hash_password


def page_profile(conn, model):
    st.markdown("""
        <div class="appbar">
          <div class="appbar-title">👤 내 정보</div>
          <div class="appbar-sub">인바디 &amp; 다이어트 목표</div>
        </div>""", unsafe_allow_html=True)

    user  = get_user(conn, st.session_state.uid) if st.session_state.uid else None
    db_ok = conn  is not None
    ai_ok = model is not None

    st.markdown(f"""
        <div class="card" style="padding:12px 16px">
          <div style="display:flex;gap:16px;font-size:0.75rem;font-weight:700">
            <span><span class="status-dot {'dot-green' if db_ok else 'dot-red'}"></span>
              {'DB 연결됨' if db_ok else '연결 없음'}</span>
            <span><span class="status-dot {'dot-green' if ai_ok else 'dot-red'}"></span>
              {'Gemini 준비' if ai_ok else 'API 키 없음'}</span>
          </div>
        </div>""", unsafe_allow_html=True)

    with st.form("profile_form", clear_on_submit=False):
        st.markdown("**기본 정보**")
        name   = st.text_input("이름", value=user.get("name","") if user else "")
        new_pw = st.text_input("비밀번호", type="password", placeholder="변경 시에만 입력")
        c1, c2 = st.columns(2)
        age    = c1.number_input("나이", 10, 100, int(user.get("age",25)) if user else 25)
        gender = c2.selectbox("성별", ["남성","여성"],
                              index=0 if not user or user.get("gender") == "남성" else 1)

        st.markdown("**인바디 측정값**")
        c1, c2 = st.columns(2)
        height = c1.number_input("키 (cm)",      100.0, 250.0, float(user.get("height",170))       if user else 170.0, 0.1)
        weight = c2.number_input("체중 (kg)",     30.0, 300.0, float(user.get("weight",70))         if user else 70.0,  0.1)
        c1, c2 = st.columns(2)
        bfat   = c1.number_input("체지방률 (%)",   1.0,  60.0, float(user.get("body_fat_pct",20))   if user else 20.0,  0.1)
        muscle = c2.number_input("골격근량 (kg)", 10.0, 100.0, float(user.get("muscle_mass",30))    if user else 30.0,  0.1)
        c1, c2 = st.columns(2)
        visc   = c1.number_input("내장지방 레벨",  1, 20,      int(user.get("visceral_fat",5))       if user else 5)
        fmass  = c2.number_input("체지방량 (kg)",  1.0, 100.0, float(user.get("body_fat_mass",10.0)) if user else 10.0,  0.1)
        act    = st.selectbox("활동량", ["거의 없음","약간","보통","활발함","매우 활발"], index=2)

        st.markdown("**다이어트 목표**")
        c1, c2 = st.columns(2)
        g_wt   = c1.number_input("목표 체중(kg)", 30.0, 300.0, float(user.get("goal_weight",65)) if user else 65.0, 0.1)
        g_day  = c2.number_input("기간(일)",       7, 365,      int(user.get("goal_days",90))     if user else 90)
        g_start = st.date_input("시작일", date.today())

        submitted = st.form_submit_button("💾 저장하기")

    if submitted:
        if not name:
            st.error("이름을 입력해주세요.")
            return
        bmr  = calc_bmr(gender, weight, height, age)
        tdee = calc_tdee(bmr, act)
        data = {
            "id": user.get("id") if user else None,
            "name": name, "age": age, "gender": gender,
            "height": height, "weight": weight,
            "body_fat_pct": bfat, "muscle_mass": muscle,
            "bmr": round(bmr, 1), "tdee": round(tdee, 1),
            "visceral_fat": visc, "body_fat_mass": fmass,
            "goal_weight": g_wt, "goal_days": g_day,
            "goal_start_date": g_start.isoformat(),
            "password": hash_password(new_pw) if new_pw else None,
        }
        uid = save_user(conn, data)
        st.session_state.uid = uid

        diff   = weight - g_wt
        days   = max(g_day, 1)
        deficit = min((diff / days) * 7, 0.5) * 7700 / 7 if diff > 0 else 0
        tgt_cal = max(tdee - deficit, bmr * 1.1)

        st.success("✅ 저장 완료!")
        st.markdown(f"""
            <div class="card" style="margin-top:12px">
              <div class="card-title">계산 결과</div>
              <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;text-align:center">
                <div style="background:#fff3ee;border-radius:12px;padding:12px 4px;border:1.5px solid #ffe5d0">
                  <div style="font-size:1.1rem;font-weight:800;color:#ff7043">{bmr:.0f}</div>
                  <div style="font-size:0.62rem;color:#b08060;margin-top:2px">BMR kcal</div>
                </div>
                <div style="background:#f0fdf6;border-radius:12px;padding:12px 4px;border:1.5px solid #c6f0da">
                  <div style="font-size:1.1rem;font-weight:800;color:#27ae74">{tdee:.0f}</div>
                  <div style="font-size:0.62rem;color:#b08060;margin-top:2px">TDEE kcal</div>
                </div>
                <div style="background:#f3ebff;border-radius:12px;padding:12px 4px;border:1.5px solid #d9c4f5">
                  <div style="font-size:1.1rem;font-weight:800;color:#9b6dea">{tgt_cal:.0f}</div>
                  <div style="font-size:0.62rem;color:#b08060;margin-top:2px">권장 kcal</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)