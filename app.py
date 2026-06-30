import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ── 페이지 설정 (반드시 가장 먼저) ──────────────────────
st.set_page_config(
    page_title="다이어트 식단 관리",
    page_icon="🥗",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS ──────────────────────────────────────────────────
from styles import MAIN_CSS, LOGIN_HERO_HTML
st.markdown(MAIN_CSS, unsafe_allow_html=True)

# ── PWA (홈 화면 추가 시 앱처럼 동작) ──────────────────────
st.markdown("""
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="DietAI">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover">
<link rel="apple-touch-icon" href="https://YOUR_DOMAIN_OR_IP/app-icon.png">
""", unsafe_allow_html=True)

# ── 리소스 초기화 ────────────────────────────────────────
from db import get_db, get_all_users, save_user
from ai import get_model
from utils import calc_bmr, calc_tdee, hash_password

conn  = get_db()
model = get_model()

# ── 세션 초기화 ──────────────────────────────────────────
for k, v in [("uid", None), ("pg", "home"), ("scan_result", None),
              ("rec_text", None), ("manual_foods", []), ("login_target", None)]:
    if k not in st.session_state:
        st.session_state[k] = v


def logout():
    st.session_state.uid         = None
    st.session_state.scan_result = None
    st.session_state.rec_text    = None
    st.session_state.manual_foods = []
    st.session_state.login_target = None
    st.session_state.pg          = "home"
    st.query_params.clear()


# ══════════════════════════════════════════════════════════
#  로그인 전: 사용자 선택 / 신규 등록
# ══════════════════════════════════════════════════════════
if st.session_state.uid is None:
    st.markdown(LOGIN_HERO_HTML, unsafe_allow_html=True)
    
    # ── 로그인 화면 상태 관리를 위한 세션 초기화 ──
    if "login_view" not in st.session_state:
        st.session_state.login_view = "landing"

    # 【스타일 1】 메인 랜딩 (대형 카드 2개 배치)
    if st.session_state.login_view == "landing":
        st.markdown("<div style='margin-top:24px;'></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        
        with c1:
            st.markdown("""
                <div style="text-align:center; padding:20px 12px; background:#fff3ee; border-radius:16px; border:1.5px solid #c6f0da; margin-bottom:-70px;">
                    <div style="font-family: 'Material Symbols Rounded'; font-size: 2.5rem; color: #27ae74;">face</div>
                    <div style="font-weight: 700; margin-top: 4px; color: #3d2c1e; font-size:0.95rem;">기존 사용자</div>
                </div>""", unsafe_allow_html=True)
            if st.button("", use_container_width=True, key="card_select", type="tertiary", help="기존 계정으로 로그인"):
                st.session_state.login_view = "select"
                st.rerun()
                
        with c2:
            st.markdown("""
                <div style="text-align:center; padding:20px 12px; background:#fff3ee; border-radius:16px; border:1.5px solid #ffe5d0; margin-bottom:-70px;">
                    <div style="font-family:'Material Symbols Rounded'; font-size:2.5rem; color:#ff7043;">person_add</div>
                    <div style="font-weight:700; margin-top:4px; color:#3d2c1e; font-size:0.95rem;">신규 등록</div>
                </div>""", unsafe_allow_html=True)
            if st.button("", use_container_width=True, key="card_new", type="tertiary", help="새로운 계정 만들기"):
                st.session_state.login_view = "new"
                st.rerun()

    # 【스타일 2】 기존 사용자 선택 UI
    elif st.session_state.login_view == "select":
        if st.button(":material/arrow_back: 뒤로가기", key="back_to_landing_1"):
            st.session_state.login_view = "landing"
            st.rerun()
            
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        if conn is None:
            st.error("DB에 연결되지 않았습니다. .env 파일의 설정을 확인해주세요.")
        else:
            users = get_all_users(conn)

            if st.session_state.login_target is None:
                for user in users:
                    if st.button(f":material/face: {user['name']}", use_container_width=True, key=f"login_{user['id']}"):
                        st.session_state.login_target = user["id"]
                        st.rerun()
            else:
                target = next((u for u in users if u["id"] == st.session_state.login_target), None)
                if target is None:
                    st.session_state.login_target = None
                    st.rerun()

                st.markdown(f"**:material/face: {target['name']}**")
                pw_input = st.text_input("비밀번호", type="password", key="login_pw")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("← 취소", use_container_width=True):
                        st.session_state.login_target = None
                        st.rerun()
                with c2:
                    if st.button("로그인", use_container_width=True, type="primary"):
                        stored_pw = target.get("password")
                        if not stored_pw:
                            st.session_state.uid = target["id"]
                            st.session_state.login_target = None
                            st.session_state.login_view = "landing"
                            st.session_state.pg = "home"
                            st.rerun()
                        elif hash_password(pw_input) == stored_pw:
                            st.session_state.uid = target["id"]
                            st.session_state.login_target = None
                            st.session_state.login_view = "landing"
                            st.session_state.pg = "home"
                            st.rerun()
                        else:
                            st.error("비밀번호가 일치하지 않습니다.")

    # 【스타일 3】 신규 회원 등록 폼 UI
    elif st.session_state.login_view == "new":
        if st.button(":material/arrow_back: 뒤로가기", key="back_to_landing_2"):
            st.session_state.login_view = "landing"
            st.rerun()
            
        st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)
        with st.form("new_user_form", clear_on_submit=False):
            st.markdown("**기본 정보**")
            new_name   = st.text_input("이름 *", placeholder="홍길동")
            new_pw     = st.text_input("비밀번호", type="password", placeholder="선택 입력")
            c1, c2     = st.columns(2)
            new_age    = c1.number_input("나이",  10, 100, 25)
            new_gender = c2.selectbox("성별", ["남성","여성"])

            st.markdown("**인바디 측정값**")
            c1, c2     = st.columns(2)
            new_height = c1.number_input("키 (cm)",      100.0, 250.0, 170.0, 0.1)
            new_weight = c2.number_input("체중 (kg)",     30.0, 300.0,  70.0, 0.1)
            c1, c2     = st.columns(2)
            new_bfat   = c1.number_input("체지방률 (%)",   1.0,  60.0,  20.0, 0.1)
            new_muscle = c2.number_input("골격근량 (kg)", 10.0, 100.0,  30.0, 0.1)
            c1, c2     = st.columns(2)
            new_visc   = c1.number_input("내장지방 레벨",  1, 20, 5)
            new_fmass  = c2.number_input("체지방량 (kg)",  1.0, 100.0, 14.0, 0.1)
            new_act    = st.selectbox("활동량", ["거의 없음","약간","보통","활발함","매우 활발"], index=2)

            st.markdown("**다이어트 목표**")
            c1, c2     = st.columns(2)
            new_gwt    = c1.number_input("목표 체중 (kg)", 30.0, 300.0, 65.0, 0.1)
            new_gday   = c2.number_input("기간 (일)",        7, 365, 90)
            from datetime import date
            new_gstart = st.date_input("시작일", date.today())

            reg_btn = st.form_submit_button(":material/how_to_reg: 등록하고 시작하기", use_container_width=True)

        if reg_btn:
            if not new_name.strip():
                st.error("이름을 입력해주세요.")
            else:
                new_bmr  = calc_bmr(new_gender, new_weight, new_height, new_age)
                new_tdee = calc_tdee(new_bmr, new_act)
                new_data = {
                    "id": None, "name": new_name.strip(), "age": new_age, "gender": new_gender,
                    "height": new_height, "weight": new_weight, "body_fat_pct": new_bfat, "muscle_mass": new_muscle,
                    "bmr": round(new_bmr, 1), "tdee": round(new_tdee, 1), "visceral_fat": new_visc, "body_fat_mass": new_fmass,
                    "goal_weight": new_gwt, "goal_days": new_gday, "goal_start_date": new_gstart.isoformat(),
                    "password": hash_password(new_pw) if new_pw else None,
                }
                try:
                    new_uid = save_user(conn, new_data)
                    if new_uid:
                        st.session_state.uid = new_uid
                        st.session_state.login_view = "landing"  # 로그인 뷰 리셋
                        st.session_state.pg  = "home"
                        st.success(f":material/check_circle: {new_name}님, 등록 완료!")
                        st.rerun()
                    else:
                        st.error("저장에 실패했습니다. DB 오류를 확인해주세요.")
                except Exception as e:
                    st.error(f"저장 오류: {e}")
# ══════════════════════════════════════════════════════════
#  로그인 후: 페이지 라우팅 + 바텀 탭바
# ══════════════════════════════════════════════════════════
else:
    from pages.home      import page_home
    from pages.scan      import page_scan
    from pages.nutrients import page_nutrients
    from pages.recommend import page_recommend
    from pages.stats     import page_stats
    from pages.profile   import page_profile

    PAGES = {
        "home":      lambda: page_home(conn, logout),
        "scan":      lambda: page_scan(conn, model),
        "stats":     lambda: page_stats(conn),
        "nutrients": lambda: page_nutrients(conn),
        "recommend": lambda: page_recommend(conn, model),
        "profile":   lambda: page_profile(conn, model),
    }
    TABS = [
        ("home",      ":material/home:", "홈"),
        ("scan",      ":material/photo_camera:", "스캔"),
        ("stats",     ":material/trending_up:", "기록"),
        ("nutrients", ":material/nutrition:", "영양소"),
        ("recommend", ":material/auto_awesome:", "추천"),
    ]

    PAGES.get(st.session_state.pg, PAGES["home"])()

    st.markdown('<div class="bottomnav">', unsafe_allow_html=True)
    tab_cols = st.columns(5)
    for i, (key, icon, label) in enumerate(TABS):
        with tab_cols[i]:
            if st.button(f"{icon}\n\n{label}", key=f"tab_{key}", use_container_width=True):
                st.session_state.pg          = key
                st.session_state.scan_result = None
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)