import json
import streamlit as st
from datetime import datetime, date
from PIL import Image
from db import get_user, save_meal
from ai import analyze_image, analyze_text
 
 
def page_scan(conn, model):
    st.markdown("""
        <div class="appbar">
          <div class="appbar-title">📸 식사 기록</div>
          <div class="appbar-sub">사진 스캔 또는 직접 입력</div>
        </div>""", unsafe_allow_html=True)
 
    if not st.session_state.uid:
        st.warning("👤 탭에서 내 정보를 먼저 입력해주세요.")
        return
    if not model:
        st.error("Gemini API 키를 설정해주세요.")
        return
 
    user = get_user(conn, st.session_state.uid)
 
    # ── 1. 사진 업로드 ──
    st.markdown("<div class='card-title'>📸 사진으로 스캔하기</div>", unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "음식 사진 (갤러리에서 선택)",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )
 
    if uploaded:
        img = Image.open(uploaded)
        st.image(img, use_container_width=True, caption="", output_format="JPEG")
 
        c1, c2 = st.columns(2)
        p_time = c1.time_input("식사 시각", value=datetime.now(), key="photo_time")
        p_type = c2.selectbox("식사 종류", ["식사", "간식"], key="photo_type")
 
        if st.session_state.scan_result is None:
            with st.spinner("🤖 사진 분석 중..."):
                result = analyze_image(model, img, user)
                if "error" not in result:
                    today_str = date.today().strftime("%Y-%m-%d")
                    result["timestamp"] = f"{today_str} {p_time.strftime('%H:%M')}"
                    result["meal_type"] = p_type
                st.session_state.scan_result = result


    # ── 2. 직접 입력 ──
    if not uploaded:
        st.markdown("<hr style='border-color:#ffe5d0;margin:24px 0'>", unsafe_allow_html=True)
        st.markdown("<div class='card-title'>✍️ 직접 입력 (AI 계산)</div>", unsafe_allow_html=True)

        # 1. 15분 단위 시각 리스트 생성 (00:00 ~ 23:45)
        time_options = []
        for h in range(24):
            for m in [0, 15, 30, 45]:
                time_options.append(f"{h:02d}:{m:02d}")
        
        # 2. 현재 시각과 가장 가까운 15분 단위 시각 계산
        now = datetime.now()
        current_minute = (now.minute // 15) * 15
        nearest_time = f"{now.hour:02d}:{current_minute:02d}"

        c1, c2    = st.columns(2)
        m_time    = c1.selectbox("식사 시각", options=time_options, index=time_options.index(nearest_time) if nearest_time in time_options else 0)
        m_type    = c2.selectbox("식사 종류", ["식사", "간식"])
        c3, c4    = st.columns(2)
        m_name    = c3.text_input("음식 종류 (예: 햇반, 구운계란)")
        m_amount  = c4.text_input("섭취량 (예: 150g, 두개)")

        if st.button("🤖 AI 영양소 계산하기"):
            if not m_name or not m_amount:
                st.warning("음식 종류와 섭취량을 입력해주세요.")
            else:
                with st.spinner("AI가 칼로리와 영양소를 계산 중입니다..."):
                    result = analyze_text(
                        model, m_name, m_amount, m_type,
                        date.today().strftime("%Y-%m-%d"),
                        m_time,
                    )
                    if "error" in result:
                        st.error(f"분석 실패: {result['error']}")
                    else:
                        st.session_state.scan_result = result

    
    # ── 3. 결과 공통 렌더링 ──
    res = st.session_state.scan_result
    if not res:
        return
 
    if "error" in res:
        st.error(f"분석 실패: {res['error']}")
        if st.button("다시 시도"):
            st.session_state.scan_result = None
            st.rerun()
        return
 
    # 타임스탬프
    ts         = res.get("timestamp")
    meal_time  = datetime.now()
    ts_badge   = ""
    if ts:
        try:
            meal_time = datetime.strptime(ts, "%Y-%m-%d %H:%M")
            ts_badge  = f'<span class="badge badge-green">📅 {ts} 기록됨</span>'
        except:
            ts_badge  = '<span class="badge badge-warn">시간 오류</span>'
 
    # 분석 헤더
    st.markdown(f"""
        <div class="analysis-header" style="margin-top:20px">
          <div class="analysis-type">{res.get('meal_type','식사')}</div>
          <div class="analysis-cal">{res.get('total_calories',0):.0f}
            <span style="font-size:1rem;color:#b08060">kcal</span>
          </div>
          <div style="margin-top:6px">{ts_badge}</div>
        </div>""", unsafe_allow_html=True)
 
    # 음식 목록
    foods = res.get("foods", [])
    if foods:
        html = '<div class="card"><div class="card-title">기록된 음식</div>'
        for f in foods:
            if isinstance(f, dict):
                html += f"""
                  <div style="display:flex;justify-content:space-between;padding:9px 0;border-bottom:1.5px solid #fff0e8">
                    <div>
                      <div style="color:#3d2c1e;font-size:0.88rem;font-weight:700">{f.get('name','')}</div>
                      <div style="color:#b08060;font-size:0.72rem">{f.get('amount','')}</div>
                    </div>
                    <div style="color:#ff7043;font-size:0.88rem;font-weight:700">{f.get('calories',0)} kcal</div>
                  </div>"""
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)
 
    # 영양소 상세
    cg = res.get("carbs_g",   0)
    pg = res.get("protein_g", 0)
    fg = res.get("fat_g",     0)
    total_mac = cg * 4 + pg * 4 + fg * 9
    c_pct = cg * 4 / total_mac * 100 if total_mac > 0 else 0
    p_pct = pg * 4 / total_mac * 100 if total_mac > 0 else 0
    f_pct = fg * 9 / total_mac * 100 if total_mac > 0 else 0
 
    st.markdown(f"""
        <div class="card">
          <div class="card-title">영양소 상세</div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px">
            <div style="text-align:center;background:#fff3ee;border-radius:14px;padding:14px 6px;border:1.5px solid #ffe5d0">
              <div style="font-size:1.3rem;font-weight:800;color:#ff7043">{cg:.0f}g</div>
              <div style="font-size:0.65rem;color:#b08060;margin-top:2px;font-weight:700">탄수화물<br>{c_pct:.0f}%</div>
            </div>
            <div style="text-align:center;background:#f0fdf6;border-radius:14px;padding:14px 6px;border:1.5px solid #c6f0da">
              <div style="font-size:1.3rem;font-weight:800;color:#27ae74">{pg:.0f}g</div>
              <div style="font-size:0.65rem;color:#b08060;margin-top:2px;font-weight:700">단백질<br>{p_pct:.0f}%</div>
            </div>
            <div style="text-align:center;background:#fdf0f8;border-radius:14px;padding:14px 6px;border:1.5px solid #f9d0ea">
              <div style="font-size:1.3rem;font-weight:800;color:#e879b8">{fg:.0f}g</div>
              <div style="font-size:0.65rem;color:#b08060;margin-top:2px;font-weight:700">지방<br>{f_pct:.0f}%</div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)
 
    if res.get("notes"):
        st.markdown(f'<div class="card" style="font-size:0.82rem;color:#7a5c47">💬 {res["notes"]}</div>',
                    unsafe_allow_html=True)
 
    # 저장 버튼
    if st.button("✅ 식사 기록 저장", type="primary"):
        meal = {
            "user_id":        user["id"],
            "meal_time":      meal_time.isoformat(),
            "meal_type":      res.get("meal_type", "식사"),
            "food_items":     res.get("foods", []),
            "total_calories": res.get("total_calories", 0),
            "carbs_g": cg, "protein_g": pg, "fat_g": fg,
            "carb_types":     res.get("carb_types", []),
            "raw_analysis":   json.dumps(res, ensure_ascii=False),
        }
        if save_meal(conn, meal):
            st.success("🎉 저장 완료!")
            st.session_state.scan_result = None
            st.rerun()
 
    if st.button("🔄 다시 입력하기"):
        st.session_state.scan_result = None
        st.rerun()
 