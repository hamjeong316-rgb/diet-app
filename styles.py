MAIN_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap');

/* ── 전체 기반 ── */
html, body, [class*="css"] {
    font-family: 'Nunito', -apple-system, BlinkMacSystemFont, sans-serif;
    -webkit-tap-highlight-color: transparent;
}
.stApp { background: #fff9f5; }

/* ── 최대 너비 모바일 고정 ── */
.block-container {
    max-width: 480px !important;
    padding: 0 16px 100px !important;
    margin: 0 auto !important;
}

/* ── 헤더 / 메뉴 숨기기 ── */
header[data-testid="stHeader"] { display: none !important; }
.stDeployButton               { display: none !important; }
#MainMenu                     { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── 앱바 ── */
.appbar {
    position: sticky; top: 0; z-index: 999;
    background: #fff9f5;
    border-bottom: 1.5px solid #ffe5d0;
    padding: 14px 0 10px;
    margin: 0 -16px 20px;
    text-align: center;
}
.appbar-title {
    font-size: 1.05rem; font-weight: 800;
    color: #3d2c1e; letter-spacing: -0.01em;
}
.appbar-sub { font-size: 0.72rem; color: #b08060; margin-top: 2px; }

/* ── 바텀 탭바 ── */
.bottomnav {
    position: fixed; bottom: 0; left: 0; right: 0; z-index: 999;
    background: #fff9f5;
    border-top: 1.5px solid #ffe5d0;
    display: flex;
    padding: 8px 0 env(safe-area-inset-bottom, 8px);
}
.nav-item {
    flex: 1; display: flex; flex-direction: column;
    align-items: center; gap: 3px; cursor: pointer;
    padding: 4px 0; font-size: 0.62rem;
    color: #c4a98a; font-weight: 700; transition: color 0.15s;
}
.nav-item.active { color: #ff7043; }
.nav-icon { font-size: 1.3rem; line-height: 1; }

/* ── 카드 ── */
.card {
    background: #ffffff;
    border: 1.5px solid #ffe5d0;
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 12px;
    box-shadow: 0 2px 10px rgba(255,112,67,0.07);
}
.card-title {
    font-size: 0.72rem; font-weight: 800;
    color: #ff7043; letter-spacing: 0.06em;
    text-transform: uppercase; margin-bottom: 12px;
}

/* ── 큰 수치 ── */
.big-num {
    font-size: 2.8rem; font-weight: 900;
    color: #3d2c1e; line-height: 1; letter-spacing: -0.03em;
}
.big-unit { font-size: 1rem; color: #b08060; margin-left: 4px; }

/* ── 미니 그리드 ── */
.mini-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.mini-card {
    background: #fff3ee; border-radius: 16px;
    border: 1.5px solid #ffe5d0;
    padding: 14px 12px; text-align: center;
}
.mini-val  { font-size: 1.4rem; font-weight: 800; color: #3d2c1e; line-height: 1; }
.mini-label { font-size: 0.68rem; color: #b08060; margin-top: 4px; font-weight: 700; }

/* ── 영양소 바 ── */
.nutr-row { margin-bottom: 13px; }
.nutr-top {
    display: flex; justify-content: space-between;
    font-size: 0.8rem; margin-bottom: 5px;
}
.nutr-name { color: #3d2c1e; font-weight: 700; }
.nutr-val  { color: #b08060; font-weight: 600; }
.bar-bg    { background: #ffe5d0; border-radius: 99px; height: 8px; }
.bar-fill  { height: 8px; border-radius: 99px; }

/* ── 식사 타임라인 ── */
.meal-item {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 0; border-bottom: 1.5px solid #fff0e8;
}
.meal-item:last-child { border-bottom: none; }
.meal-dot-wrap {
    display: flex; flex-direction: column;
    align-items: center; padding-top: 5px;
}
.meal-dot {
    width: 9px; height: 9px; border-radius: 50%;
    background: #ff7043; flex-shrink: 0;
}
.meal-line { width: 1px; flex: 1; background: #ffe5d0; margin-top: 4px; min-height: 20px; }
.meal-time-label { font-size: 0.7rem; color: #c4a98a; min-width: 44px; padding-top: 3px; font-weight: 700; }
.meal-name { font-size: 0.88rem; color: #3d2c1e; font-weight: 700; }
.meal-cal  { font-size: 0.74rem; color: #ff7043; margin-top: 2px; font-weight: 700; }
.meal-macro { font-size: 0.7rem; color: #b08060; margin-top: 1px; }

/* ── 진행바 ── */
.progress-wrap { margin-bottom: 6px; }
.progress-bg   { background: #ffe5d0; border-radius: 99px; height: 8px; }
.progress-fill {
    height: 8px; border-radius: 99px;
    background: linear-gradient(90deg, #ff7043, #ffa270);
}

/* ── 배지 ── */
.badge {
    display: inline-block; padding: 4px 10px;
    border-radius: 99px; font-size: 0.7rem;
    font-weight: 800; margin: 2px;
}
.badge-blue   { background: #e8f0ff; color: #4d7cfe; }
.badge-green  { background: #e6faf2; color: #27ae74; }
.badge-purple { background: #f3ebff; color: #9b6dea; }
.badge-warn   { background: #fff3e0; color: #f59e0b; }

/* ── 폼 입력 ── */
.stTextInput input, .stNumberInput input {
    background: #fff9f5 !important;
    border: 1.5px solid #ffe5d0 !important;
    border-radius: 12px !important;
    color: #3d2c1e !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    padding: 10px 12px !important;
}
.stSelectbox > div > div {
    background: #fff9f5 !important;
    border: 1.5px solid #ffe5d0 !important;
    border-radius: 12px !important;
    color: #3d2c1e !important;
    font-weight: 600 !important;
}
.stSelectbox label {
    font-size: 0.85rem !important;
}
.stSelectbox div[data-baseweb="select"] {
    font-size: 0.85rem !important;
    height: 42px !important;
}
div[role="listbox"] span {
    font-size: 0.85rem !important;
}
label, .stMarkdown p { color: #7a5c47 !important; font-size: 0.85rem !important; font-weight: 700 !important; }

/* ── 버튼 ── */
.stButton > button {
    background: linear-gradient(135deg, #ff7043, #ff9a6c) !important;
    color: #fff !important; border: none !important;
    border-radius: 14px !important;
    font-weight: 800 !important; font-size: 0.9rem !important;
    padding: 10px !important; width: 100% !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 4px 16px rgba(255,112,67,0.25) !important;
    transition: transform 0.1s !important;
}
.stButton > button:active { transform: scale(0.97) !important; }
div[data-testid="stButton"] > button[key*="card_select"] {
    background-color: transparent !important;
    border: none !important;
}

/* ── 파일 업로더 ── */
[data-testid="stFileUploader"] {
    background: #fff9f5;
    border: 2px dashed #ffb89a;
    border-radius: 20px;
    padding: 16px;
}
[data-testid="stFileUploadDropzone"] { padding: 20px 0; }

/* ── 탭 숨기기 (로그인 후) ── */
.stTabs { display: none; }

/* ── 제목 ── */
h1, h2, h3 { color: #3d2c1e !important; }
.section-gap { margin-top: 24px; }

/* ── 추천 결과 박스 ── */
.rec-box {
    background: #fff9f5;
    border: 1.5px solid #ffe5d0;
    border-radius: 20px; padding: 20px;
    font-size: 0.85rem; color: #3d2c1e; line-height: 1.8;
    box-shadow: 0 2px 10px rgba(255,112,67,0.07);
}
.rec-box strong { color: #ff7043; }
.rec-box h3, .rec-box h4 { color: #3d2c1e !important; font-size: 0.95rem !important; }

/* ── 분석 결과 헤더 ── */
.analysis-header {
    background: linear-gradient(135deg, #fff3ee, #ffe5d0);
    border-radius: 18px; padding: 18px; margin-bottom: 12px;
    border: 1.5px solid #ffe5d0;
}
.analysis-type {
    font-size: 0.7rem; color: #ff7043;
    text-transform: uppercase; letter-spacing: 0.08em; font-weight: 800;
}
.analysis-cal {
    font-size: 2.4rem; font-weight: 900;
    color: #3d2c1e; line-height: 1; margin: 4px 0;
}

/* ── 스크롤바 ── */
::-webkit-scrollbar { width: 0; background: transparent; }

/* ── 상태 dot ── */
.status-dot {
    display: inline-block; width: 6px; height: 6px;
    border-radius: 50%; margin-right: 5px; vertical-align: middle;
}
.dot-green { background: #27ae74; }
.dot-red   { background: #ef4444; }
</style>
"""



LOGIN_HERO_HTML = """
<div style="text-align:center; padding: 48px 0 28px;">
    <div style="font-size:3.5rem; margin-bottom:10px">🥗</div>
    <div style="font-size:1.5rem; font-weight:900; color:#3d2c1e; margin-bottom:6px">DietAI</div>
    <div style="font-size:0.82rem; color:#b08060; font-weight:700">맞춤 식단 관리 시작하기 🌿</div>
</div>
"""
