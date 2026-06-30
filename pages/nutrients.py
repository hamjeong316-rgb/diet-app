import streamlit as st
import plotly.graph_objects as go
from db import get_user, get_today_meals
from utils import target_calories, sum_nutrients


def page_nutrients(conn):
    st.markdown("""
        <div class="appbar">
          <div class="appbar-title"><span style="font-family:'Material Symbols Rounded';vertical-align:middle;margin-right:4px;">leaderboard</span> 오늘 영양소 현황</div>
          <div class="appbar-sub">목표 대비 달성률을 확인해요</div>
        </div>""", unsafe_allow_html=True)

    if not st.session_state.uid:
        st.warning("내 정보를 먼저 입력해주세요.")
        return

    user    = get_user(conn, st.session_state.uid)
    meals   = get_today_meals(conn, user["id"])
    tgt_cal = target_calories(user)
    n       = sum_nutrients(meals)
    tgt_c   = tgt_cal * 0.5  / 4
    tgt_p   = tgt_cal * 0.25 / 4
    tgt_f   = tgt_cal * 0.25 / 9

    if not meals:
        st.markdown(
            '<div class="card" style="text-align:center;padding:32px">'
            '<p style="color:#b08060; display:flex; flex-direction:column; align-items:center; gap:4px;">'
            '  <span><span style="font-family:\'Material Symbols Rounded\'; vertical-align:middle; margin-right:4px;">restaurant</span>오늘 식사 기록이 없어요</span>'
            '  <span style="font-size:0.85rem; color:#b08060; opacity:0.8;"><span style="font-family:\'Material Symbols Rounded\'; vertical-align:middle; margin-right:4px; font-size:1.1rem;">photo_camera</span>스캔 탭에서 업로드해보세요</span>'
            '</p></div>',
            unsafe_allow_html=True,
        )

    # ── 칼로리 게이지 ──
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=n["calories"],
        title={"text": "오늘 섭취 / 목표 kcal", "font": {"color": "#b08060", "size": 13}},
        number={"font": {"color": "#3d2c1e", "size": 36}, "suffix": " kcal"},
        gauge={
            "axis": {"range": [0, tgt_cal * 1.3], "tickcolor": "#ffe5d0",
                     "tickfont": {"color": "#b08060", "size": 10}},
            "bar": {"color": "#ff7043", "thickness": 0.7},
            "bgcolor": "#ffe5d0",
            "bordercolor": "#ffe5d0",
            "steps": [
                {"range": [0, tgt_cal * 0.7],          "color": "#fff3ee"},
                {"range": [tgt_cal * 0.7, tgt_cal],    "color": "#ffe5d0"},
                {"range": [tgt_cal, tgt_cal * 1.3],    "color": "#ffd0c0"},
            ],
            "threshold": {"line": {"color": "#ff7043", "width": 2}, "value": tgt_cal},
        },
    ))
    fig.update_layout(
        paper_bgcolor="#ffffff",
        font_color="#3d2c1e",
        height=200,
        margin=dict(t=40, b=10, l=20, r=20),
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    # ── 영양소 목표 달성 바 ──
    nutrients = [
        ("🌾 탄수화물", n["carbs"],   tgt_c, "#ff7043"),
        ("🥩 단백질",   n["protein"], tgt_p, "#27ae74"),
        ("🥑 지방",     n["fat"],     tgt_f, "#e879b8"),
    ]
    html = '<div class="card"><div class="card-title">영양소 목표 달성</div>'
    for name, curr, tgt, color in nutrients:
        pct  = min(curr / tgt * 100, 100) if tgt > 0 else 0
        over = curr > tgt
        html += f"""
          <div class="nutr-row">
            <div class="nutr-top">
              <span class="nutr-name">{name}</span>
              <span class="nutr-val" style="color:{'#f87171' if over else '#b08060'}">{curr:.0f}g / {tgt:.0f}g ({pct:.0f}%)</span>
            </div>
            <div class="bar-bg"><div class="bar-fill" style="width:{pct:.0f}%;background:{color}"></div></div>
          </div>"""
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    # ── 탄수화물 종류 배지 ──
    all_ct = []
    for m in meals:
        ct = m.get("carb_types", [])
        if isinstance(ct, list):
            all_ct.extend(ct)
    if all_ct:
        badges = "".join(f'<span class="badge badge-blue">{c}</span>' for c in all_ct)
        st.markdown(
            f'<div class="card"><div class="card-title">오늘 탄수화물 종류</div>{badges}</div>',
            unsafe_allow_html=True,
        )

    # ── 도넛 차트 ──
    if meals:
        mac_vals = [n["carbs"] * 4, n["protein"] * 4, n["fat"] * 9]
        if sum(mac_vals) > 0:
            fig2 = go.Figure(go.Pie(
                labels=["탄수화물", "단백질", "지방"],
                values=mac_vals, hole=0.65,
                marker_colors=["#ff7043", "#27ae74", "#e879b8"],
                textinfo="label+percent",
                textfont=dict(color="#ffffff", size=11),
                showlegend=False,
            ))
            fig2.update_layout(
                paper_bgcolor="#ffffff", height=220,
                margin=dict(t=20, b=10, l=10, r=10),
                annotations=[dict(text="구성", x=0.5, y=0.5,
                                  font_size=13, font_color="#b08060", showarrow=False)],
            )
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
