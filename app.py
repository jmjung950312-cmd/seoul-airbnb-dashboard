"""
서울 에어비앤비 RevPAR 최적화 대시보드
Airbnb-style BI Dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── 페이지 설정 ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="서울 Airbnb RevPAR 대시보드",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── 브랜드 색상 ───────────────────────────────────────────────────────────────
AIRBNB_RED   = "#FF5A5F"
AIRBNB_PINK  = "#FF8589"
AIRBNB_LIGHT = "#FFCDD2"
AIRBNB_DARK  = "#C0392B"
TEAL         = "#2A9D8F"
AMBER        = "#F4A261"
GREEN        = "#00B894"

CLUSTER_COLORS = {
    "프리미엄 관광거점": AIRBNB_RED,
    "성장형 주거상권":   "#E17055",
    "중가 균형시장":     AMBER,
    "가격민감 외곽형":   AIRBNB_PINK,
}

# ── 글로벌 CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* 전체 배경 */
.main .block-container {
    padding: 0.8rem 2rem 2rem 2rem;
    max-width: 1500px;
}

/* ── 헤더 ── */
.airbnb-header {
    background: linear-gradient(120deg, #FF5A5F 0%, #C0392B 100%);
    padding: 18px 28px;
    border-radius: 12px;
    margin-bottom: 14px;
}
.brand-logo {
    font-size: 2rem;
    font-weight: 900;
    color: white;
    letter-spacing: -0.5px;
    line-height: 1;
}
.brand-title {
    font-size: 1.15rem;
    font-weight: 700;
    color: white;
    margin-top: 2px;
}
.brand-sub {
    font-size: 0.78rem;
    color: rgba(255,255,255,0.82);
    margin-top: 3px;
}

/* ── KPI 카드 ── */
.kpi-card {
    background: white;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    border-left: 5px solid #FF5A5F;
    height: 100%;
    min-height: 90px;
}
.kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #FF5A5F;
    line-height: 1.1;
}
.kpi-label {
    font-size: 0.75rem;
    color: #777;
    margin-top: 4px;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

/* ── 스코어 카드 ── */
.score-card {
    background: #FF5A5F;
    border-radius: 10px;
    padding: 14px 12px;
    text-align: center;
    color: white;
    height: 100%;
    min-height: 75px;
}
.score-value {
    font-size: 1.7rem;
    font-weight: 800;
    color: white;
    line-height: 1.1;
}
.score-label {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.92);
    margin-top: 3px;
    font-weight: 500;
}

/* ── 섹션 타이틀 ── */
.section-title {
    font-size: 0.88rem;
    font-weight: 700;
    color: #333;
    margin: 0 0 6px 0;
    padding-bottom: 5px;
    border-bottom: 2px solid #FF5A5F;
    text-transform: uppercase;
    letter-spacing: 0.4px;
}

/* ── 인사이트 텍스트 박스 ── */
.insight-box {
    font-size: 0.78rem;
    color: #444;
    background: #FFF5F5;
    border-left: 3px solid #FF5A5F;
    padding: 6px 10px;
    border-radius: 4px;
    margin-bottom: 6px;
    line-height: 1.4;
}

/* ── 필터 바 ── */
.filter-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #555;
    text-transform: uppercase;
    margin-bottom: 2px;
}

/* ── 분리선 ── */
hr { border-color: #f0f0f0 !important; margin: 14px 0 !important; }

/* streamlit 기본 패딩 제거 */
div[data-testid="stVerticalBlock"] > div { padding-top: 0 !important; }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
#  데이터 로딩 & 전처리 (캐싱)
# ════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner="데이터 로딩 중…")
def load_raw() -> pd.DataFrame:
    df = pd.read_csv("data/raw/seoul_airbnb_cleaned.csv")
    df["is_ao"] = (df["refined_status"] == "Active") & (
        df["operation_status"] == "Operating"
    )
    return df


@st.cache_data(show_spinner="자치구 데이터 로딩 중…")
def load_district() -> pd.DataFrame:
    return pd.read_csv("data/processed/district_clustered.csv")


@st.cache_data
def compute_kpis(df: pd.DataFrame) -> dict:
    ao = df[df["is_ao"]]
    sh_rev  = ao[ao["superhost"] == True]["ttm_revpar"].median()
    nsh_rev = ao[ao["superhost"] == False]["ttm_revpar"].median()
    return {
        "total":             len(df),
        "ao_count":          len(ao),
        "dormant_pct":       df["refined_status"].isin(["Dormant","Ghost"]).mean() * 100,
        "median_revpar_all": df["ttm_revpar"].median(),
        "median_revpar_ao":  ao["ttm_revpar"].median(),
        "superhost_revpar":  sh_rev,
        "non_superhost_revpar": nsh_rev,
        "sh_premium_pct":    (sh_rev / nsh_rev - 1) * 100,
        "total_revenue":     df["ttm_revenue"].sum(),
        "avg_rating":        ao["rating_overall"].median(),
        "superhost_pct":     ao["superhost"].mean() * 100,
        "instant_book_pct":  ao["instant_book"].mean() * 100,
        "ao_pct":            len(ao) / len(df) * 100,
    }


@st.cache_data
def compute_photo_bins(df: pd.DataFrame) -> pd.DataFrame:
    ao = df[df["is_ao"] & df["photos_count"].notna()].copy()
    ao["photo_bin"] = pd.cut(
        ao["photos_count"],
        bins=[0, 10, 20, 35, 50, 75, 100, 200, 2000],
        labels=["1-10","11-20","21-35","36-50","51-75","76-100","101-200","200+"],
    )
    return ao.groupby("photo_bin", observed=True)["ttm_revpar"].median().reset_index()


@st.cache_data
def compute_min_nights_bins(df: pd.DataFrame) -> pd.DataFrame:
    ao = df[df["is_ao"] & (df["min_nights"] <= 30)].copy()
    ao["mn_bin"] = pd.cut(
        ao["min_nights"],
        bins=[0, 1, 2, 3, 7, 14, 30],
        labels=["1박","2박","3박","4-7박","8-14박","15-30박"],
    )
    return ao.groupby("mn_bin", observed=True)["ttm_revpar"].median().reset_index()


@st.cache_data
def map_sample(df: pd.DataFrame, n: int = 5000) -> pd.DataFrame:
    cols = ["latitude_masked","longitude_masked","room_type","ttm_revpar",
            "district","superhost","is_ao"]
    sub = df[df["latitude_masked"].notna() & df["longitude_masked"].notna()][cols]
    return sub.sample(min(n, len(sub)), random_state=42)


# ════════════════════════════════════════════════════════════════════════
#  데이터 로딩
# ════════════════════════════════════════════════════════════════════════
raw_df  = load_raw()
dist_df = load_district()
kpis    = compute_kpis(raw_df)


# ════════════════════════════════════════════════════════════════════════
#  ① 헤더 (Airbnb 브랜드)
# ════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="airbnb-header">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <div>
      <div class="brand-logo">∞ airbnb</div>
      <div class="brand-title">데이터 분석 · 서울</div>
      <div class="brand-sub">
        TTM 12개월 (2024-10 ~ 2025-09) &nbsp;·&nbsp;
        32,061개 리스팅 &nbsp;·&nbsp; 25개 자치구
      </div>
    </div>
    <div style="text-align:right; color:rgba(255,255,255,0.9); font-size:0.82rem;">
      RevPAR 최적화 분석<br>
      <span style="font-size:0.72rem; opacity:0.8;">Seoul Airbnb Analytics · 2026</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════
#  ② 필터 바
# ════════════════════════════════════════════════════════════════════════
with st.container():
    f0, f1, f2, f3, f4 = st.columns([1.6, 1.6, 1.6, 1.6, 5])

    with f0:
        st.markdown('<div class="filter-label">분석 범위</div>', unsafe_allow_html=True)
        data_scope = st.selectbox(
            "분석범위",
            ["Active+Operating", "전체 리스팅"],
            index=0,
            label_visibility="collapsed",
        )

    with f1:
        st.markdown('<div class="filter-label">룸 타입</div>', unsafe_allow_html=True)
        room_options = ["전체"] + sorted(raw_df["room_type"].dropna().unique().tolist())
        sel_room = st.selectbox("룸타입", room_options, label_visibility="collapsed")

    with f2:
        st.markdown('<div class="filter-label">슈퍼호스트</div>', unsafe_allow_html=True)
        sh_filter = st.selectbox(
            "슈퍼호스트",
            ["전체", "슈퍼호스트", "일반 호스트"],
            label_visibility="collapsed",
        )

    with f3:
        st.markdown('<div class="filter-label">즉시예약</div>', unsafe_allow_html=True)
        ib_filter = st.selectbox(
            "즉시예약",
            ["전체", "즉시예약 ON", "즉시예약 OFF"],
            label_visibility="collapsed",
        )

    with f4:
        st.markdown('<div class="filter-label">자치구 선택 (비우면 전체)</div>', unsafe_allow_html=True)
        all_districts = sorted(dist_df["district"].dropna().tolist())
        sel_districts = st.multiselect(
            "자치구",
            options=all_districts,
            default=[],
            placeholder="자치구를 선택하세요…",
            label_visibility="collapsed",
        )

# ── 필터 적용 ─────────────────────────────────────────────────────────────────
view_df = raw_df[raw_df["is_ao"]].copy() if data_scope == "Active+Operating" else raw_df.copy()
if sel_room != "전체":
    view_df = view_df[view_df["room_type"] == sel_room]
if sh_filter == "슈퍼호스트":
    view_df = view_df[view_df["superhost"] == True]
elif sh_filter == "일반 호스트":
    view_df = view_df[view_df["superhost"] == False]
if ib_filter == "즉시예약 ON":
    view_df = view_df[view_df["instant_book"] == True]
elif ib_filter == "즉시예약 OFF":
    view_df = view_df[view_df["instant_book"] == False]
if sel_districts:
    view_df  = view_df[view_df["district"].isin(sel_districts)]
    dist_view = dist_df[dist_df["district"].isin(sel_districts)]
else:
    dist_view = dist_df.copy()

ao_df = raw_df[raw_df["is_ao"]].copy()
if sel_districts:
    ao_df = ao_df[ao_df["district"].isin(sel_districts)]

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
#  ③ KPI 카드 (상단 4개)
# ════════════════════════════════════════════════════════════════════════
k1, k2, k3, k4 = st.columns(4)

with k1:
    rev_b = kpis["total_revenue"] / 1e9
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">₩{rev_b:.1f}B</div>
        <div class="kpi-label">총 TTM 수익 (서울 전체)</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color:#E17055;">
        <div class="kpi-value" style="color:#E17055;">{kpis['total']:,}개</div>
        <div class="kpi-label">전체 리스팅 수</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color:#2D3436;">
        <div class="kpi-value" style="color:#2D3436;">{kpis['ao_count']:,}개</div>
        <div class="kpi-label">Active + Operating</div>
    </div>""", unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color:{GREEN};">
        <div class="kpi-value" style="color:{GREEN};">₩{kpis['median_revpar_ao']:,.0f}</div>
        <div class="kpi-label">중위 RevPAR (Active+Operating)</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

# ── 스코어 카드 6개 ────────────────────────────────────────────────────────────
sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
score_data = [
    (sc1, f"{kpis['avg_rating']:.2f}",          "평균 평점",          AIRBNB_RED),
    (sc2, f"{kpis['superhost_pct']:.1f}%",       "슈퍼호스트 비율",    "#E17055"),
    (sc3, f"+{kpis['sh_premium_pct']:.0f}%",     "슈퍼호스트 프리미엄", AIRBNB_DARK),
    (sc4, f"{kpis['dormant_pct']:.1f}%",         "Dormant 비율",       "#636e72"),
    (sc5, f"{kpis['instant_book_pct']:.1f}%",    "즉시예약 비율",       AMBER),
    (sc6, f"{kpis['ao_pct']:.1f}%",              "활성 운영 비율",      TEAL),
]
for col, val, label, bg in score_data:
    with col:
        st.markdown(f"""
        <div class="score-card" style="background:{bg};">
            <div class="score-value">{val}</div>
            <div class="score-label">{label}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
st.markdown("---")


# ════════════════════════════════════════════════════════════════════════
#  ④ 메인 차트 Row 1 — 자치구 RevPAR / 리스팅 수 / 룸타입
# ════════════════════════════════════════════════════════════════════════
col_l, col_c, col_r = st.columns([2.2, 2.2, 1.6])

# ── 자치구별 중위 RevPAR (수평 막대) ─────────────────────────────────────────
with col_l:
    st.markdown('<div class="section-title">자치구별 중위 RevPAR · Active+Operating</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="insight-box">종로구·용산구·강남구가 RevPAR 상위권 — '
        '마포구는 공급 1위(21%)지만 RevPAR 압박 구조</div>',
        unsafe_allow_html=True,
    )
    dist_bar = (
        raw_df[raw_df["is_ao"]]
        .groupby("district")["ttm_revpar"]
        .median()
        .sort_values(ascending=True)
        .reset_index()
    )
    if sel_districts:
        dist_bar = dist_bar[dist_bar["district"].isin(sel_districts)]

    fig = go.Figure(go.Bar(
        x=dist_bar["ttm_revpar"],
        y=dist_bar["district"],
        orientation="h",
        marker_color=AIRBNB_RED,
        text=dist_bar["ttm_revpar"].apply(lambda v: f"₩{v:,.0f}"),
        textposition="outside",
        textfont=dict(size=9),
    ))
    fig.update_layout(
        height=max(430, len(dist_bar) * 20),
        margin=dict(l=0, r=90, t=6, b=0),
        xaxis=dict(showgrid=True, gridcolor="#f5f5f5", title=""),
        yaxis=dict(showgrid=False, title=""),
        plot_bgcolor="white", paper_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)

# ── 자치구별 리스팅 수 ─────────────────────────────────────────────────────────
with col_c:
    st.markdown('<div class="section-title">자치구별 리스팅 수 · 공급량</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="insight-box">마포구가 전체 공급의 약 21% — '
        '공급 집중도와 RevPAR 간 역상관 관계 주목</div>',
        unsafe_allow_html=True,
    )
    dist_cnt = (
        raw_df.groupby("district")
        .size()
        .sort_values(ascending=True)
        .reset_index(name="count")
    )
    if sel_districts:
        dist_cnt = dist_cnt[dist_cnt["district"].isin(sel_districts)]

    fig2 = go.Figure(go.Bar(
        x=dist_cnt["count"],
        y=dist_cnt["district"],
        orientation="h",
        marker_color=AIRBNB_PINK,
        text=dist_cnt["count"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(size=9),
    ))
    fig2.update_layout(
        height=max(430, len(dist_cnt) * 20),
        margin=dict(l=0, r=60, t=6, b=0),
        xaxis=dict(showgrid=True, gridcolor="#f5f5f5", title=""),
        yaxis=dict(showgrid=False, title=""),
        plot_bgcolor="white", paper_bgcolor="white",
    )
    st.plotly_chart(fig2, use_container_width=True)

# ── 룸 타입 파이 + 수익 막대 ───────────────────────────────────────────────────
with col_r:
    st.markdown('<div class="section-title">룸 타입 구성 비율</div>',
                unsafe_allow_html=True)
    rt_count = view_df["room_type"].value_counts().reset_index()
    rt_count.columns = ["room_type", "count"]
    fig3 = px.pie(
        rt_count,
        values="count", names="room_type",
        color_discrete_sequence=[AIRBNB_RED, AIRBNB_PINK, AMBER, "#DFE6E9"],
        hole=0.42,
        template="plotly_white",
    )
    fig3.update_layout(
        height=230,
        margin=dict(l=0, r=0, t=6, b=0),
        legend=dict(orientation="v", x=0.62, y=0.5, font=dict(size=9)),
        showlegend=True,
    )
    fig3.update_traces(texttemplate="%{percent:.1%}", textposition="inside",
                       textfont_size=9)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-title" style="margin-top:8px;">룸 타입별 중위 RevPAR</div>',
                unsafe_allow_html=True)
    rt_rev = (
        view_df.groupby("room_type")["ttm_revpar"]
        .median()
        .sort_values(ascending=False)
        .reset_index()
    )
    fig4 = px.bar(
        rt_rev,
        x="room_type", y="ttm_revpar",
        color="room_type",
        color_discrete_sequence=[AIRBNB_RED, AIRBNB_PINK, AMBER, "#DFE6E9"],
        labels={"ttm_revpar": "RevPAR (₩)", "room_type": ""},
        template="plotly_white",
        text="ttm_revpar",
    )
    fig4.update_traces(texttemplate="₩%{text:,.0f}", textposition="outside",
                       textfont_size=8)
    fig4.update_layout(
        height=220, showlegend=False,
        margin=dict(l=0, r=0, t=6, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis_tickfont_size=9,
    )
    st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════
#  ⑤ 호스트 드라이버 분석 Row 2
# ════════════════════════════════════════════════════════════════════════
st.markdown(
    '<h3 style="color:#333; font-weight:800; font-size:1rem; margin:0 0 10px 0; '
    f'border-left:4px solid {AIRBNB_RED}; padding-left:10px;">'
    "호스트 RevPAR 드라이버 분석</h3>",
    unsafe_allow_html=True,
)

col_a, col_b, col_c2 = st.columns(3)
photo_data = compute_photo_bins(raw_df)
mn_data    = compute_min_nights_bins(raw_df)

# ── 사진 수 ────────────────────────────────────────────────────────────────────
with col_a:
    st.markdown('<div class="section-title">사진 수 구간별 중위 RevPAR</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="insight-box">21~35장이 최적 구간 — 이상은 한계효용 체감</div>',
        unsafe_allow_html=True,
    )
    bins   = photo_data["photo_bin"].tolist()
    colors = [AIRBNB_LIGHT] * len(bins)
    if "21-35" in bins:
        colors[bins.index("21-35")] = AIRBNB_RED

    fig5 = go.Figure(go.Bar(
        x=bins,
        y=photo_data["ttm_revpar"],
        marker_color=colors,
        text=photo_data["ttm_revpar"].apply(lambda v: f"₩{v:,.0f}"),
        textposition="outside",
        textfont=dict(size=8),
    ))
    if "21-35" in bins:
        opt_val = photo_data.loc[photo_data["photo_bin"]=="21-35","ttm_revpar"].values[0]
        fig5.add_annotation(
            x="21-35", y=opt_val * 1.18,
            text="★ 최적", showarrow=False,
            font=dict(color=AIRBNB_RED, size=10, family="Arial Black"),
        )
    fig5.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=6, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False, title="사진 수", tickfont_size=9),
        yaxis=dict(showgrid=True, gridcolor="#f5f5f5", title=""),
    )
    st.plotly_chart(fig5, use_container_width=True)

# ── 최소숙박일 ──────────────────────────────────────────────────────────────────
with col_b:
    st.markdown('<div class="section-title">최소숙박일별 중위 RevPAR</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="insight-box">2~3박 최적점 — 장기 숙박은 RevPAR 하락</div>',
        unsafe_allow_html=True,
    )
    mn_bins   = mn_data["mn_bin"].tolist()
    mn_colors = [AIRBNB_LIGHT] * len(mn_bins)
    for opt in ["2박", "3박"]:
        if opt in mn_bins:
            mn_colors[mn_bins.index(opt)] = AIRBNB_RED

    fig6 = go.Figure(go.Bar(
        x=mn_bins,
        y=mn_data["ttm_revpar"],
        marker_color=mn_colors,
        text=mn_data["ttm_revpar"].apply(lambda v: f"₩{v:,.0f}"),
        textposition="outside",
        textfont=dict(size=8),
    ))
    fig6.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=6, b=0),
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False, title="최소숙박일", tickfont_size=9),
        yaxis=dict(showgrid=True, gridcolor="#f5f5f5", title=""),
    )
    st.plotly_chart(fig6, use_container_width=True)

# ── 슈퍼호스트 × 즉시예약 ────────────────────────────────────────────────────────
with col_c2:
    st.markdown('<div class="section-title">슈퍼호스트 × 즉시예약 RevPAR</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="insight-box">슈퍼호스트+즉시예약 조합이 최고 RevPAR 달성</div>',
        unsafe_allow_html=True,
    )
    cross = (
        ao_df.groupby(["superhost", "instant_book"])["ttm_revpar"]
        .median()
        .reset_index()
    )
    cross["호스트"] = cross["superhost"].map({True: "슈퍼호스트", False: "일반 호스트"})
    cross["즉시예약"] = cross["instant_book"].map({True: "ON", False: "OFF"})
    fig7 = px.bar(
        cross,
        x="호스트", y="ttm_revpar",
        color="즉시예약",
        barmode="group",
        labels={"ttm_revpar": "RevPAR (₩)"},
        color_discrete_map={"ON": AIRBNB_RED, "OFF": AIRBNB_LIGHT},
        template="plotly_white",
        text="ttm_revpar",
    )
    fig7.update_traces(texttemplate="₩%{text:,.0f}", textposition="outside",
                       textfont_size=8)
    fig7.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=6, b=0),
        legend=dict(orientation="h", y=1.08, font=dict(size=10)),
        plot_bgcolor="white", paper_bgcolor="white",
    )
    st.plotly_chart(fig7, use_container_width=True)

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════
#  ⑥ 군집 분석 + 지도 + 리스팅 상태 파이
# ════════════════════════════════════════════════════════════════════════
st.markdown(
    '<h3 style="color:#333; font-weight:800; font-size:1rem; margin:0 0 10px 0; '
    f'border-left:4px solid {AIRBNB_RED}; padding-left:10px;">'
    "자치구 군집 분석 (K-Means k=4)</h3>",
    unsafe_allow_html=True,
)

col_bubble, col_map, col_pie2 = st.columns([1.8, 2.2, 1])

# ── 군집 버블 차트 ─────────────────────────────────────────────────────────────
with col_bubble:
    st.markdown('<div class="section-title">공급량 vs RevPAR 포지셔닝</div>',
                unsafe_allow_html=True)
    fig_b = px.scatter(
        dist_view,
        x="total_listings", y="median_revpar_ao",
        size="ao_count", color="cluster_name",
        text="district",
        hover_data={"total_listings":":,","median_revpar_ao":":,.0f","dormant_ratio":":.1%"},
        labels={"total_listings":"리스팅 수","median_revpar_ao":"중위 RevPAR (₩)","cluster_name":"군집"},
        color_discrete_map=CLUSTER_COLORS,
        template="plotly_white",
        size_max=50,
    )
    fig_b.update_traces(textposition="top center", textfont_size=9)
    fig_b.update_layout(
        height=420,
        margin=dict(l=0, r=0, t=6, b=0),
        legend=dict(orientation="h", y=-0.18, font=dict(size=9)),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_b, use_container_width=True)

# ── 서울 리스팅 지도 ─────────────────────────────────────────────────────────────
with col_map:
    st.markdown('<div class="section-title">서울 리스팅 분포 지도 (샘플 5,000)</div>',
                unsafe_allow_html=True)
    map_df = map_sample(raw_df)
    fig_map = px.scatter_mapbox(
        map_df,
        lat="latitude_masked",
        lon="longitude_masked",
        color="room_type",
        color_discrete_sequence=[AIRBNB_RED, AIRBNB_PINK, AMBER, "#74B9FF"],
        hover_data={"district": True, "ttm_revpar": ":,.0f", "room_type": True,
                    "latitude_masked": False, "longitude_masked": False},
        labels={"room_type": "룸 타입"},
        opacity=0.55,
        zoom=10.5,
        center={"lat": 37.5665, "lon": 126.9780},
        mapbox_style="open-street-map",
        template="plotly_white",
    )
    fig_map.update_layout(
        height=420,
        margin=dict(l=0, r=0, t=6, b=0),
        legend=dict(orientation="h", y=-0.12, font=dict(size=9)),
    )
    st.plotly_chart(fig_map, use_container_width=True)

# ── 리스팅 상태 파이 + 군집 요약 ──────────────────────────────────────────────
with col_pie2:
    st.markdown('<div class="section-title">리스팅 상태 분포</div>',
                unsafe_allow_html=True)
    status_cnt = raw_df["refined_status"].value_counts()
    fig_s = px.pie(
        values=status_cnt.values, names=status_cnt.index,
        color_discrete_sequence=[AIRBNB_RED, AIRBNB_PINK, AMBER, "#DFE6E9"],
        hole=0.45,
        template="plotly_white",
    )
    fig_s.update_layout(
        height=210,
        margin=dict(l=0, r=0, t=6, b=0),
        legend=dict(orientation="v", x=0.55, y=0.5, font=dict(size=9)),
    )
    fig_s.update_traces(texttemplate="%{percent:.1%}", textposition="inside",
                        textfont_size=9)
    st.plotly_chart(fig_s, use_container_width=True)

    st.markdown('<div class="section-title" style="margin-top:8px;">군집 요약</div>',
                unsafe_allow_html=True)
    csumm = (
        dist_view.groupby("cluster_name")
        .agg(N=("district","count"), RevPAR=("median_revpar_ao","median"))
        .reset_index()
        .sort_values("RevPAR", ascending=False)
    )
    for _, row in csumm.iterrows():
        clr = CLUSTER_COLORS.get(row["cluster_name"], AIRBNB_RED)
        st.markdown(
            f"<div style='border-left:3px solid {clr}; padding:4px 8px; margin:4px 0; "
            f"background:#fafafa; border-radius:3px; font-size:0.75rem;'>"
            f"<b style='color:{clr}'>{row['cluster_name']}</b><br>"
            f"{row['N']}개 자치구 &nbsp;·&nbsp; ₩{row['RevPAR']:,.0f}</div>",
            unsafe_allow_html=True,
        )

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════
#  ⑦ TTM vs L90D RevPAR 트렌드 + Dormant 비율
# ════════════════════════════════════════════════════════════════════════
col_tr, col_dm = st.columns(2)

with col_tr:
    st.markdown('<div class="section-title">자치구별 TTM vs L90D RevPAR · 최근 성장 트렌드</div>',
                unsafe_allow_html=True)
    growth = (
        raw_df[raw_df["is_ao"]]
        .groupby("district")
        .agg(ttm=("ttm_revpar","median"), l90=("l90d_revpar","median"))
        .reset_index()
        .sort_values("ttm", ascending=False)
    )
    if sel_districts:
        growth = growth[growth["district"].isin(sel_districts)]

    fig_tr = go.Figure()
    fig_tr.add_trace(go.Bar(
        name="TTM 중위 RevPAR",
        x=growth["district"], y=growth["ttm"],
        marker_color=AIRBNB_RED,
        text=growth["ttm"].apply(lambda v: f"₩{v:,.0f}"),
        textposition="outside", textfont=dict(size=7),
    ))
    fig_tr.add_trace(go.Bar(
        name="L90D 중위 RevPAR",
        x=growth["district"], y=growth["l90"],
        marker_color=AIRBNB_PINK,
        text=growth["l90"].apply(lambda v: f"₩{v:,.0f}"),
        textposition="outside", textfont=dict(size=7),
    ))
    fig_tr.update_layout(
        barmode="group",
        height=360,
        template="plotly_white",
        margin=dict(l=0, r=0, t=6, b=80),
        xaxis_tickangle=-45, xaxis_tickfont_size=9,
        legend=dict(orientation="h", y=-0.3, font=dict(size=10)),
        yaxis_title="중위 RevPAR (₩)",
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_tr, use_container_width=True)

with col_dm:
    st.markdown('<div class="section-title">자치구별 Dormant 비율</div>',
                unsafe_allow_html=True)
    st.markdown(
        '<div class="insight-box">전체 Dormant 54.3% — 시장 건전성 핵심 리스크</div>',
        unsafe_allow_html=True,
    )
    dorm = dist_view.sort_values("dormant_ratio", ascending=True).copy()
    dorm["위험"] = dorm["dormant_ratio"].apply(
        lambda x: "고위험 (>60%)" if x > 0.6
        else ("중위험 (40-60%)" if x > 0.4 else "저위험 (<40%)")
    )
    risk_map = {"고위험 (>60%)": AIRBNB_RED, "중위험 (40-60%)": AMBER, "저위험 (<40%)": GREEN}
    fig_dm = px.bar(
        dorm,
        x="dormant_ratio", y="district",
        orientation="h",
        color="위험",
        color_discrete_map=risk_map,
        labels={"dormant_ratio": "Dormant 비율", "district": ""},
        template="plotly_white",
        text="dormant_ratio",
    )
    fig_dm.update_traces(texttemplate="%{text:.1%}", textposition="outside",
                         textfont_size=8)
    fig_dm.update_layout(
        height=360,
        margin=dict(l=0, r=60, t=6, b=0),
        xaxis_tickformat=".0%",
        legend=dict(orientation="h", y=-0.18, font=dict(size=10)),
        plot_bgcolor="white",
    )
    st.plotly_chart(fig_dm, use_container_width=True)

st.markdown("---")


# ════════════════════════════════════════════════════════════════════════
#  ⑧ 군집 히트맵 + 자치구 상세 테이블
# ════════════════════════════════════════════════════════════════════════
col_heat, col_tbl = st.columns([1.5, 2.5])

with col_heat:
    st.markdown('<div class="section-title">군집별 특성 프로파일 (정규화)</div>',
                unsafe_allow_html=True)
    num_cols = ["median_revpar_ao","dormant_ratio","superhost_rate","supply_share","ao_count"]
    lbl_map  = {
        "median_revpar_ao": "중위 RevPAR",
        "dormant_ratio":    "Dormant 비율",
        "superhost_rate":   "슈퍼호스트율",
        "supply_share":     "공급 비중",
        "ao_count":         "A+O 수",
    }
    cp = dist_view.groupby("cluster_name")[num_cols].mean().reset_index()
    cn = cp.copy()
    for c in num_cols:
        mn, mx = cn[c].min(), cn[c].max()
        cn[c] = (cn[c] - mn) / (mx - mn + 1e-9)

    fig_heat = go.Figure(go.Heatmap(
        z=cn[num_cols].values,
        x=[lbl_map[c] for c in num_cols],
        y=cn["cluster_name"].tolist(),
        colorscale="RdBu",
        reversescale=True,
        text=[[f"{v:.2f}" for v in row] for row in cn[num_cols].values],
        texttemplate="%{text}",
        showscale=True,
    ))
    fig_heat.update_layout(
        height=280,
        template="plotly_white",
        margin=dict(l=0, r=0, t=6, b=0),
        xaxis_tickfont_size=9,
        yaxis_tickfont_size=9,
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with col_tbl:
    st.markdown('<div class="section-title">자치구 상세 현황</div>',
                unsafe_allow_html=True)
    disp = {
        "district":        "자치구",
        "cluster_name":    "군집",
        "total_listings":  "전체 리스팅",
        "ao_count":        "A+O 수",
        "median_revpar_ao":"중위 RevPAR",
        "dormant_ratio":   "Dormant 비율",
        "superhost_rate":  "슈퍼호스트율",
        "supply_share":    "공급 비중",
    }
    tdf = dist_view[list(disp.keys())].rename(columns=disp).copy()
    tdf["중위 RevPAR"]   = tdf["중위 RevPAR"].apply(lambda v: f"₩{v:,.0f}")
    tdf["Dormant 비율"]  = tdf["Dormant 비율"].apply(lambda v: f"{v:.1%}")
    tdf["슈퍼호스트율"]    = tdf["슈퍼호스트율"].apply(lambda v: f"{v:.1%}")
    tdf["공급 비중"]      = tdf["공급 비중"].apply(lambda v: f"{v:.1%}")
    st.dataframe(tdf, use_container_width=True, hide_index=True, height=280)
