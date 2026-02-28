import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform

# ── 페이지 설정 ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="에어비앤비 수익 최적화",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── 한글 폰트 ─────────────────────────────────────────────────────────────────
def set_korean_font():
    system = platform.system()
    if system == "Darwin":
        candidates = ["AppleGothic", "Apple SD Gothic Neo", "Arial Unicode MS"]
    elif system == "Windows":
        candidates = ["Malgun Gothic", "NanumGothic", "Gulim"]
    else:
        candidates = ["NanumGothic", "NanumBarunGothic", "UnDotum"]
    available = [f.name for f in fm.fontManager.ttflist]
    for font in candidates:
        if font in available:
            plt.rcParams["font.family"] = font
            plt.rcParams["axes.unicode_minus"] = False
            return font
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    return "default"

set_korean_font()

# ── Airbnb 스타일 CSS ─────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  /* 전체 배경 & 폰트 */
  .stApp {
    background-color: #FFF9F7;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif !important;
  }
  .stApp * {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif !important;
  }

  /* 메인 컨테이너 */
  .block-container {
    max-width: 860px !important;
    padding: 1.5rem 2rem 3rem !important;
  }

  /* 사이드바 숨기기 */
  [data-testid="stSidebar"] { display: none !important; }
  [data-testid="collapsedControl"] { display: none !important; }

  /* CTA 버튼 (다음 단계, 분석 결과 보기, 처음부터) */
  .stButton > button {
    background-color: #FF5A5F !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 11px 24px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.1px !important;
    width: 100% !important;
    cursor: pointer !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 2px 6px rgba(255,90,95,0.25) !important;
  }
  .stButton > button:hover {
    background-color: #E8474C !important;
    box-shadow: 0 4px 12px rgba(255,90,95,0.35) !important;
    transform: translateY(-1px) !important;
  }
  .stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 1px 4px rgba(255,90,95,0.2) !important;
  }

  /* 뒤로가기 버튼 — ghost/outline 스타일 */
  .back-btn .stButton > button {
    background-color: transparent !important;
    color: #717171 !important;
    border: 1.5px solid #DDDDDD !important;
    box-shadow: none !important;
  }
  .back-btn .stButton > button:hover {
    background-color: #F7F7F7 !important;
    border-color: #AAAAAA !important;
    color: #484848 !important;
    transform: none !important;
    box-shadow: none !important;
  }

  /* 숙소 종류 선택 버튼 — 선택 안 된 상태 */
  .room-type-btn .stButton > button {
    background-color: white !important;
    color: #484848 !important;
    border: 1.5px solid #E0E0E0 !important;
    text-align: left !important;
    font-weight: 500 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
  }
  .room-type-btn .stButton > button:hover {
    border-color: #FF5A5F !important;
    color: #FF5A5F !important;
    background-color: #FFF8F8 !important;
    transform: none !important;
    box-shadow: 0 2px 6px rgba(255,90,95,0.1) !important;
  }

  /* 숙소 종류 선택 버튼 — 선택된 상태 */
  .room-type-btn-selected .stButton > button {
    background-color: #FFF0EE !important;
    color: #FF5A5F !important;
    border: 2px solid #FF5A5F !important;
    font-weight: 700 !important;
    box-shadow: 0 2px 8px rgba(255,90,95,0.18) !important;
  }
  .room-type-btn-selected .stButton > button:hover {
    background-color: #FFE8E8 !important;
    transform: none !important;
  }

  /* 카드 공통 */
  .card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06);
    margin-bottom: 16px;
  }

  /* 구분선 */
  .section-divider {
    border: none;
    border-top: 1px solid #EBEBEB;
    margin: 32px 0;
  }

  /* 숫자 하이라이트 */
  .big-num { font-size: 30px; font-weight: 800; color: #FF5A5F; }

  /* 숨기기 */
  #MainMenu { visibility: hidden; }
  footer { visibility: hidden; }

  /* selectbox, number_input */
  .stSelectbox > div > div,
  .stNumberInput > div > div > input {
    border-radius: 8px !important;
  }

  /* 체크박스 간격 */
  .stCheckbox { margin-bottom: 6px; }

  /* 헤더 타이포그래피 */
  h3 { letter-spacing: -0.3px !important; }
</style>
""", unsafe_allow_html=True)

# ── 상수 ─────────────────────────────────────────────────────────────────────
DISTRICT_KR = {
    "Gangnam-gu": "강남구", "Gangdong-gu": "강동구", "Gangbuk-gu": "강북구",
    "Gangseo-gu": "강서구", "Gwanak-gu": "관악구", "Gwangjin-gu": "광진구",
    "Guro-gu": "구로구", "Geumcheon-gu": "금천구", "Nowon-gu": "노원구",
    "Dobong-gu": "도봉구", "Dongdaemun-gu": "동대문구", "Dongjak-gu": "동작구",
    "Mapo-gu": "마포구", "Seodaemun-gu": "서대문구", "Seocho-gu": "서초구",
    "Seongdong-gu": "성동구", "Seongbuk-gu": "성북구", "Songpa-gu": "송파구",
    "Yangcheon-gu": "양천구", "Yeongdeungpo-gu": "영등포구", "Yongsan-gu": "용산구",
    "Eunpyeong-gu": "은평구", "Jongno-gu": "종로구", "Jung-gu": "중구",
    "Jungnang-gu": "중랑구",
}

ROOM_TYPE_KR = {
    "entire_home": "집 전체",
    "private_room": "개인실",
    "hotel_room": "호텔 객실",
    "shared_room": "다인실",
}
ROOM_TYPE_DESC = {
    "entire_home": "숙소 전체를 단독으로 사용하는 형태",
    "private_room": "침실은 개인 공간, 거실·주방은 공용",
    "hotel_room": "호텔 스타일 객실",
    "shared_room": "다른 게스트와 공간을 함께 사용",
}

CLUSTER_INFO = {
    "핫플 수익형": {
        "emoji": "🏆", "color": "#FF5A5F",
        "elasticity": -0.7,
        "desc": "관광·상권이 집중된 핫플 지역으로 수요가 탄탄해 요금을 올려도 예약이 잘 줄지 않습니다.",
        "strategy": [
            "1박 요금 10~20% 인상 테스트 — 수요가 탄탄합니다",
            "즉시예약 반드시 켜기 — 예약 기회를 놓치지 마세요",
            "사진 20~35장 + 주변 관광지 포함 촬영",
            "영문 설명 최적화 — 외국인 게스트 유입",
            "슈퍼호스트 달성 후 요금 프리미엄 적용",
        ],
    },
    "로컬 주거형": {
        "emoji": "🏡", "color": "#00A699",
        "elasticity": -0.9,
        "desc": "주거 중심 생활권으로 장기 체류·재방문 수요가 안정적인 지역입니다.",
        "strategy": [
            "현재 요금 수준 방어 — 불필요한 가격 인하 자제",
            "슈퍼호스트 + 게스트 선호 배지 달성 목표",
            "평점 4.8 이상 유지 — 리뷰 관리에 집중",
            "집 전체 형태 전환 검토 — 개인실 대비 수익 2.7배",
            "지하철역·생활 편의시설 근접성을 설명에 명시",
        ],
    },
    "가성비 신흥형": {
        "emoji": "⚖️", "color": "#FFB400",
        "elasticity": -1.1,
        "desc": "가격 대비 가치를 중시하는 게스트가 많은 신흥 지역입니다. 운영 최적화가 핵심입니다.",
        "strategy": [
            "사진 20~35장 등록 — 클릭률 높이기가 1순위",
            "최소 숙박 2~3박 — 리뷰를 빠르게 쌓는 전략",
            "즉시예약 켜기 — 비용 없이 예약률 높이기",
            "추가 게스트 요금 없애고 1박 요금에 통합",
            "슈퍼호스트 달성 후 요금 소폭 인상",
        ],
    },
    "프리미엄 비즈니스": {
        "emoji": "💼", "color": "#3F51B5",
        "elasticity": -0.8,
        "desc": "비즈니스·고급 관광 수요가 높은 프리미엄 지역으로 높은 ADR과 RevPAR를 기대할 수 있습니다.",
        "strategy": [
            "요금 인상 여력 있음 — 지역 상위 25% 요금 목표",
            "비즈니스 편의시설(Wi-Fi, 업무 공간)을 강조",
            "슈퍼호스트 배지 필수 — 프리미엄 포지셔닝",
            "영문·중문 설명 최적화 — 해외 비즈니스 게스트 유입",
            "평일 수요 높음 — 주중 요금 강화 전략",
        ],
    },
}

POI_TYPES = ["관광지", "문화시설", "쇼핑", "음식점", "숙박", "레포츠", "여행코스"]

# ── 데이터 로드 ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("data/raw/final_seoul_airbnb_cleaned.csv")
    cluster_df = pd.read_csv("data/processed/district_clustered.csv")
    df = df.merge(
        cluster_df[["district", "cluster", "cluster_name"]],
        on="district", how="left",
    )
    return df, cluster_df

df, cluster_df = load_data()
active_df = df[
    (df["refined_status"] == "Active") & (df["operation_status"] == "Operating")
].copy()

# ── ML 모델 로드 ──────────────────────────────────────────────────────────────
@st.cache_resource
def load_ml_models():
    try:
        from predict_utils import load_models
        return load_models()
    except Exception:
        return None


@st.cache_data
def compute_district_stats(_active_df, _cluster_df):
    """자치구별 ML 피처 구성에 필요한 통계 딕셔너리 반환."""
    pop_map = _cluster_df.set_index("district")["median_pop"].to_dict()
    result = {}
    for district, grp in _active_df.groupby("district"):
        entire_mask = grp["room_type"] == "entire_home"
        result[district] = {
            "median_revpar":          float(grp["ttm_revpar"].median()),
            "listing_count":          len(grp),
            "superhost_rate":         float(grp["superhost"].mean()) if "superhost" in grp.columns else 0.25,
            "entire_home_rate":       float(entire_mask.mean()),
            "photos_mean":            float(grp["photos_count"].mean()) if "photos_count" in grp.columns else 22.0,
            "rating_mean":            float(grp["rating_overall"].mean()) if "rating_overall" in grp.columns else 4.7,
            "reviews_mean":           float(grp["num_reviews"].mean()) if "num_reviews" in grp.columns else 20.0,
            "min_nights_mean":        float(grp["min_nights"].mean()) if "min_nights" in grp.columns else 2.0,
            "cluster":                int(grp["cluster"].mode().iloc[0]) if "cluster" in grp.columns and len(grp) > 0 else 2,
            "ttm_pop_mode":           int(pop_map.get(district, 100_000)),
        }
    return result


# ── 헬퍼 ─────────────────────────────────────────────────────────────────────
def get_bench(district, room_type):
    return active_df[
        (active_df["district"] == district) &
        (active_df["room_type"] == room_type)
    ]

def bench_val(bench, col, default, pct=50):
    if len(bench) > 0 and col in bench.columns:
        vals = bench[col].dropna()
        if len(vals) > 0:
            return float(np.percentile(vals, pct))
    return default

def dn(district):
    """district 영문 → 한국어"""
    return DISTRICT_KR.get(district, district)

# ── session_state 초기화 ──────────────────────────────────────────────────────
def init_state():
    defaults = {
        "step": 1,
        "district": "Mapo-gu",
        "room_type": "entire_home",
        "my_adr": None,
        "my_occ_pct": None,
        "opex_elec": 80000,
        "opex_water": 30000,
        "opex_mgmt": 150000,
        "opex_net": 30000,
        "opex_clean": 200000,
        "opex_loan": 0,
        "opex_etc": 50000,
        "my_bedrooms": None,
        "my_baths": None,
        "my_guests": None,
        "my_photos": None,
        "my_superhost": False,
        "my_instant": False,
        "my_extra_fee": False,
        "my_min_nights": None,
        "my_rating": None,
        "my_reviews": None,
        "my_poi_dist": None,
        "my_500m": None,
        "my_poi_type": "관광지",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── 공통 UI 컴포넌트 ─────────────────────────────────────────────────────────
def render_logo():
    st.markdown("""
    <div style="text-align:center;padding:28px 0 8px;">
      <div style="font-size:30px;margin-bottom:10px;">🏠</div>
      <h2 style="color:#FF5A5F;margin:0 0 6px;font-weight:800;letter-spacing:-0.6px;font-size:26px;">
        에어비앤비 수익 최적화
      </h2>
      <p style="color:#9CA3AF;font-size:13px;margin:0;font-weight:400;">
        서울 실운영 숙소 14,399개 데이터 기반 · 내 숙소 맞춤 분석
      </p>
    </div>
    """, unsafe_allow_html=True)

def render_progress(current):
    labels = ["숙소 정보", "요금 현황", "월 운영비", "운영 체크"]
    html = '<div style="display:flex;align-items:flex-start;justify-content:center;gap:0;margin:20px 0 32px;">'
    for i, label in enumerate(labels, 1):
        if i < current:
            circle_bg, circle_color, line_color = "#FF5A5F", "white", "#FF5A5F"
            circle_content = "✓"
        elif i == current:
            circle_bg, circle_color, line_color = "#FF5A5F", "white", "#EBEBEB"
            circle_content = str(i)
        else:
            circle_bg, circle_color, line_color = "#EBEBEB", "#AAAAAA", "#EBEBEB"
            circle_content = str(i)

        label_color = "#FF5A5F" if i == current else ("#484848" if i < current else "#AAAAAA")
        html += '<div style="display:flex;flex-direction:column;align-items:center;flex:1;">'
        html += (
            f'<div style="display:flex;align-items:center;width:100%;">'
            f'<div style="flex:1;height:2px;background:{"transparent" if i==1 else line_color};"></div>'
            f'<div style="width:32px;height:32px;border-radius:50%;background:{circle_bg};'
            f'color:{circle_color};display:flex;align-items:center;justify-content:center;'
            f'font-size:13px;font-weight:700;flex-shrink:0;">{circle_content}</div>'
            f'<div style="flex:1;height:2px;background:{"transparent" if i==4 else "#EBEBEB"};"></div>'
            f'</div>'
        )
        html += f'<div style="font-size:11px;color:{label_color};margin-top:5px;font-weight:{"600" if i==current else "400"};">{label}</div>'
        html += "</div>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def card_open():
    st.markdown('<div class="card">', unsafe_allow_html=True)

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)

def section_title(title, subtitle=""):
    sub = f'<p style="color:#717171;font-size:13px;margin:4px 0 16px;line-height:1.5;">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<h3 style="color:#222222;margin:0 0 4px;font-weight:700;letter-spacing:-0.3px;font-size:18px;">{title}</h3>{sub}',
        unsafe_allow_html=True,
    )

def coral_box(content):
    st.markdown(
        f'<div style="background:#FFF0EE;border-radius:10px;padding:16px 20px;margin-top:8px;">{content}</div>',
        unsafe_allow_html=True,
    )

def info_row(label, value, value_color="#484848"):
    st.markdown(
        f'<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #F5F5F5;">'
        f'<span style="color:#767676;font-size:14px;">{label}</span>'
        f'<span style="font-weight:600;color:{value_color};font-size:14px;">{value}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── ML 피처 유틸리티 ──────────────────────────────────────────────────────────
def get_photos_tier(n):
    """훈련 데이터 기준: 하(<14) | 중하(14-22) | 중상(23-35 최적) | 상(36+)"""
    if n < 14:   return "하"
    if n <= 22:  return "중하"
    if n <= 35:  return "중상"
    return "상"


def get_poi_dist_category(km):
    """훈련 데이터 기준: 초근접(<0.2) | 근접(0.2-0.5) | 보통(0.5-1.0) | 원거리(1.0+)"""
    if km < 0.2:  return "초근접"
    if km < 0.5:  return "근접"
    if km < 1.0:  return "보통"
    return "원거리"


def build_listing_features(ss, dist_stats):
    """session_state + 자치구 통계 → predict_revpar() 입력 dict 조립."""
    district = ss.district
    d = dist_stats.get(district, {})

    photos_mean    = d.get("photos_mean", 22.0)
    rating_mean    = d.get("rating_mean", 4.7)
    reviews_mean   = d.get("reviews_mean", 20.0)
    min_nights_mean = d.get("min_nights_mean", 2.0)

    my_photos     = int(ss.my_photos or 20)
    my_rating     = float(ss.my_rating or 4.7)
    my_reviews    = int(ss.my_reviews or 10)
    my_min_nights = int(ss.my_min_nights or 2)
    my_poi_dist   = float(ss.my_poi_dist or 0.3)
    my_adr        = float(ss.my_adr or 100_000)
    my_bedrooms   = int(ss.get("my_bedrooms") or 1)
    my_baths      = float(ss.get("my_baths") or 1.0)
    my_guests     = int(ss.get("my_guests") or 2)

    return {
        # Model A
        "cluster":                    d.get("cluster", 2),
        "nearest_poi_dist_km":        my_poi_dist,
        "poi_dist_category":          get_poi_dist_category(my_poi_dist),
        "bedrooms":                   my_bedrooms,
        "baths":                      my_baths,
        "guests":                     my_guests,
        "room_type":                  ss.room_type,  # encoder trained on snake_case values
        "nearest_poi_type_name":      ss.my_poi_type,
        "district_median_revpar":     d.get("median_revpar", 40_000),
        "district_listing_count":     d.get("listing_count", 100),
        "district_superhost_rate":    d.get("superhost_rate", 0.25),
        "district_entire_home_rate":  d.get("entire_home_rate", 0.7),
        "ttm_pop":                    d.get("ttm_pop_mode", 100_000),
        # Model B
        "min_nights":              my_min_nights,
        "instant_book":            1 if bool(ss.my_instant) else 0,
        "superhost":               1 if bool(ss.my_superhost) else 0,
        "rating_overall":          my_rating,
        "photos_count":            my_photos,
        "num_reviews":             my_reviews,
        "extra_guest_fee_policy":  "1" if bool(ss.my_extra_fee) else "0",
        "photos_tier":             get_photos_tier(my_photos),
        "is_active_operating":     1,
        # Relative competitiveness
        "photos_rel_dist":    min(5.0, max(0.0, my_photos / max(photos_mean, 1))),
        "rating_rel_dist":    min(5.0, max(0.0, my_rating / max(rating_mean, 0.1))),
        "reviews_rel_dist":   min(5.0, max(0.0, my_reviews / max(reviews_mean, 1))),
        "min_nights_rel_dist": min(5.0, max(0.0, my_min_nights / max(min_nights_mean, 1))),
        # ADR (for price_gap inside predict_revpar)
        "ttm_avg_rate": my_adr,
    }


def compute_health_score(user_vals, cluster_listings):
    """클러스터 내 백분위 기반 5-컴포넌트 헬스 스코어 (0~100)."""
    def pct_rank(value, series):
        s = series.dropna()
        return float(np.mean(s <= value) * 100) if len(s) > 0 else 50.0

    # 1. Review Signal
    reviews_pct = pct_rank(user_vals["my_reviews"], cluster_listings["num_reviews"])
    rating_pct  = pct_rank(user_vals["my_rating"],  cluster_listings["rating_overall"])
    review_signal = (reviews_pct + rating_pct) / 2

    # 2. Listing Quality — 사진 최적 구간 23-35
    n = user_vals["my_photos"]
    if 23 <= n <= 35:
        photos_score = 100.0
    elif n < 23:
        photos_score = (n / 23) * 100
    else:
        photos_score = max(0.0, 100.0 - (n - 35) * 2.5)
    listing_quality = photos_score

    # 3. Booking Policy
    instant_score = 100.0 if user_vals["my_instant"] else 0.0
    min_nights_pct = (
        pct_rank(user_vals["my_min_nights"], cluster_listings["min_nights"])
        if "min_nights" in cluster_listings.columns else 50.0
    )
    no_extra_fee_score = 100.0 if not user_vals["my_extra_fee"] else 0.0
    booking_policy = 0.4 * instant_score + 0.4 * (100 - min_nights_pct) + 0.2 * no_extra_fee_score

    # 4. Location — 거리 낮을수록 좋음
    poi_dist_pct = (
        pct_rank(user_vals["my_poi_dist"], cluster_listings["nearest_poi_dist_km"])
        if "nearest_poi_dist_km" in cluster_listings.columns else 50.0
    )
    location = 100 - poi_dist_pct

    # 5. Listing Config
    bedrooms_pct = (
        pct_rank(user_vals["my_bedrooms"], cluster_listings["bedrooms"])
        if "bedrooms" in cluster_listings.columns else 50.0
    )
    baths_pct = (
        pct_rank(user_vals["my_baths"], cluster_listings["baths"])
        if "baths" in cluster_listings.columns else 50.0
    )
    listing_config = (bedrooms_pct + baths_pct) / 2

    composite = (review_signal + listing_quality + booking_policy + location + listing_config) / 5

    if composite >= 80:   grade = "A"
    elif composite >= 60: grade = "B"
    elif composite >= 40: grade = "C"
    elif composite >= 20: grade = "D"
    else:                 grade = "F"

    return {
        "composite": composite,
        "grade": grade,
        "components": {
            "review_signal":   review_signal,
            "listing_quality": listing_quality,
            "booking_policy":  booking_policy,
            "location":        location,
            "listing_config":  listing_config,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — 내 숙소 정보
# ═══════════════════════════════════════════════════════════════════════════════
def step1():
    render_logo()
    render_progress(1)
    section_title("1단계: 내 숙소 기본 정보", "내 숙소의 위치와 종류를 선택해주세요.")

    col1, col2 = st.columns(2)

    with col1:
        districts = sorted(df["district"].dropna().unique())
        options = [f"{DISTRICT_KR.get(d, d)}" for d in districts]
        default_idx = districts.index("Mapo-gu") if "Mapo-gu" in districts else 0
        sel_idx = st.selectbox("📍 자치구", options, index=default_idx)
        st.session_state.district = districts[options.index(sel_idx)]

        # 선택 구 미리보기
        bench = get_bench(st.session_state.district, st.session_state.room_type)
        if len(bench) > 0:
            med = bench_val(bench, "ttm_revpar", 40000)
            coral_box(
                f'<span style="font-size:12px;color:#888;">이 지역 실운영 숙소 평균 하루 수익</span><br>'
                f'<span style="font-size:22px;font-weight:700;color:#FF5A5F;">₩{int(med):,}</span>'
                f'<span style="font-size:12px;color:#888;"> / 박 기준 ({len(bench):,}개 숙소)</span>'
            )

    with col2:
        st.markdown("**🏠 숙소 종류**")
        room_types = sorted(df["room_type"].dropna().unique())
        for rt in room_types:
            selected = st.session_state.room_type == rt
            check = "✓  " if selected else ""
            label = f"{check}{ROOM_TYPE_KR.get(rt, rt)} — {ROOM_TYPE_DESC.get(rt, '')}"
            btn_class = "room-type-btn-selected" if selected else "room-type-btn"
            st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
            if st.button(label, key=f"rt_{rt}", use_container_width=True):
                st.session_state.room_type = rt
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # ── 숙소 규모 입력 ─────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("**🛏️ 숙소 규모**")
    bench_spec = get_bench(st.session_state.district, st.session_state.room_type)
    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        default_bd = int(st.session_state.my_bedrooms) if st.session_state.my_bedrooms is not None else max(1, int(bench_val(bench_spec, "bedrooms", 1)))
        my_bedrooms = st.number_input("침실 수", min_value=0, max_value=20, value=default_bd, step=1)
        st.session_state.my_bedrooms = my_bedrooms
    with sc2:
        default_bt = float(st.session_state.my_baths) if st.session_state.my_baths is not None else round(bench_val(bench_spec, "baths", 1.0), 1)
        my_baths = st.number_input("욕실 수", min_value=0.0, max_value=10.0, value=default_bt, step=0.5)
        st.session_state.my_baths = my_baths
    with sc3:
        default_gs = int(st.session_state.my_guests) if st.session_state.my_guests is not None else max(1, int(bench_val(bench_spec, "guests", 2)))
        my_guests = st.number_input("최대 인원", min_value=1, max_value=30, value=default_gs, step=1)
        st.session_state.my_guests = my_guests

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("다음 단계 →", key="next1", use_container_width=True):
        st.session_state.step = 2
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — 요금 & 예약률
# ═══════════════════════════════════════════════════════════════════════════════
def step2():
    render_logo()
    render_progress(2)
    section_title(
        "2단계: 내 숙소 요금 & 예약률",
        "현재 1박 요금과 예약률을 입력해주세요. 에어비앤비 앱 → 인사이트에서 확인할 수 있어요.",
    )

    bench = get_bench(st.session_state.district, st.session_state.room_type)
    b_adr = bench_val(bench, "ttm_avg_rate", 100000)
    b_occ = bench_val(bench, "ttm_occupancy", 0.40)

    # 지역 평균 참고 박스
    d_name = dn(st.session_state.district)
    rt_name = ROOM_TYPE_KR.get(st.session_state.room_type, "")
    st.markdown(
        f'<div style="background:#F7F7F7;border-radius:10px;padding:14px 18px;margin-bottom:16px;">'
        f'<span style="font-size:13px;font-weight:600;color:#484848;">'
        f'📊 {d_name} {rt_name} — 지역 평균 참고값</span><br>'
        f'<span style="font-size:13px;color:#767676;">'
        f'평균 1박 요금 <b>₩{int(b_adr):,}</b> &nbsp;|&nbsp; 평균 예약률 <b>{b_occ:.0%}</b>'
        f'</span></div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        default_adr = int(st.session_state.my_adr) if st.session_state.my_adr else int(b_adr)
        my_adr = st.number_input(
            "💰 현재 1박 요금 (원)",
            min_value=0, max_value=2_000_000,
            value=default_adr, step=5_000,
            help="에어비앤비에 설정한 기본 1박 요금을 입력하세요",
        )
        st.session_state.my_adr = my_adr

    with col2:
        default_occ = int(st.session_state.my_occ_pct) if st.session_state.my_occ_pct else int(b_occ * 100)
        my_occ_pct = st.slider(
            "📅 한 달 예약률 (%)",
            0, 100, default_occ,
            help="한 달 30일 중 실제 예약이 들어온 날의 비율입니다",
        )
        st.session_state.my_occ_pct = my_occ_pct

    my_revpar = my_adr * (my_occ_pct / 100)
    coral_box(
        f'<div style="text-align:center;">'
        f'<span style="font-size:13px;color:#888;">내 하루 평균 실수익 (요금 × 예약률)</span><br>'
        f'<span class="big-num">₩{int(my_revpar):,}</span>'
        f'<span style="font-size:14px;color:#888;"> / 박</span>'
        f'</div>'
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← 이전", key="back2", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        if st.button("다음 단계 →", key="next2", use_container_width=True):
            st.session_state.step = 3
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — 월 운영비
# ═══════════════════════════════════════════════════════════════════════════════
def step3():
    render_logo()
    render_progress(3)
    section_title(
        "3단계: 월 운영비 입력",
        "숙소를 운영하는 데 매달 고정으로 나가는 비용을 입력해주세요. 본전 요금 계산에 사용됩니다.",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔌 공과금 · 관리비**")
        opex_elec  = st.number_input("전기세 (원/월)",  0, 500_000,   st.session_state.opex_elec,  5_000)
        opex_water = st.number_input("수도세 (원/월)",  0, 200_000,   st.session_state.opex_water, 5_000)
        opex_mgmt  = st.number_input("관리비 (원/월)",  0, 1_000_000, st.session_state.opex_mgmt,  10_000)
        opex_net   = st.number_input("인터넷 (원/월)",  0, 100_000,   st.session_state.opex_net,   5_000)
        st.session_state.opex_elec  = opex_elec
        st.session_state.opex_water = opex_water
        st.session_state.opex_mgmt  = opex_mgmt
        st.session_state.opex_net   = opex_net

    with col2:
        st.markdown("**🧹 청소 · 대출 · 기타**")
        opex_clean = st.number_input("청소 비용 (원/월)",  0, 1_000_000, st.session_state.opex_clean, 10_000)
        opex_loan  = st.number_input("대출 이자 (원/월)", 0, 5_000_000, st.session_state.opex_loan,  50_000)
        opex_etc   = st.number_input("기타 비용 (원/월)", 0, 500_000,   st.session_state.opex_etc,   10_000)
        st.session_state.opex_clean = opex_clean
        st.session_state.opex_loan  = opex_loan
        st.session_state.opex_etc   = opex_etc

    total_opex = (opex_elec + opex_water + opex_mgmt + opex_net
                  + opex_clean + opex_loan + opex_etc)

    coral_box(
        f'<div style="display:flex;justify-content:space-between;align-items:center;">'
        f'<span style="font-size:14px;color:#888;">월 총 운영비</span>'
        f'<span class="big-num">₩{total_opex:,}</span>'
        f'</div>'
        f'<div style="font-size:12px;color:#AAA;margin-top:4px;">에어비앤비 수수료 3%는 별도입니다</div>'
    )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← 이전", key="back3", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        if st.button("다음 단계 →", key="next3", use_container_width=True):
            st.session_state.step = 4
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 4 — 운영 현황 체크
# ═══════════════════════════════════════════════════════════════════════════════
def step4():
    render_logo()
    render_progress(4)
    section_title(
        "4단계: 운영 현황 체크",
        "현재 숙소 운영 상태를 체크해주세요. 개선 포인트를 정확히 찾는 데 사용됩니다.",
    )

    bench = get_bench(st.session_state.district, st.session_state.room_type)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**⭐ 리뷰 & 평점**")
        default_rv = int(st.session_state.my_reviews) if st.session_state.my_reviews is not None else int(bench_val(bench, "num_reviews", 20))
        my_reviews = st.number_input("현재 리뷰 수 (건)", 0, 5000, default_rv, help="에어비앤비 앱에서 확인한 총 리뷰 수")
        st.session_state.my_reviews = my_reviews

        default_rt = float(st.session_state.my_rating) if st.session_state.my_rating is not None else round(bench_val(bench, "rating_overall", 4.70), 1)
        my_rating = st.slider("현재 평점", 0.0, 5.0, default_rt, 0.1)
        st.session_state.my_rating = my_rating

        st.markdown("**🏅 배지 & 예약 설정**")
        my_superhost = st.checkbox(
            "슈퍼호스트 배지 있음",
            value=bool(st.session_state.my_superhost),
            help="에어비앤비에서 슈퍼호스트 배지를 보유하고 있으면 체크",
        )
        st.session_state.my_superhost = my_superhost

        my_instant = st.checkbox(
            "즉시예약 켜져 있음",
            value=bool(st.session_state.my_instant),
            help="게스트가 호스트 승인 없이 바로 예약할 수 있는 기능",
        )
        st.session_state.my_instant = my_instant

        my_extra_fee = st.checkbox(
            "추가 게스트 요금 받고 있음",
            value=bool(st.session_state.my_extra_fee),
            help="기본 인원 초과 시 1인당 추가 요금을 받는 설정",
        )
        st.session_state.my_extra_fee = my_extra_fee

    with col2:
        st.markdown("**📸 사진 & 숙박 설정**")
        default_ph = int(st.session_state.my_photos) if st.session_state.my_photos is not None else int(bench_val(bench, "photos_count", 22))
        my_photos = st.number_input("등록된 사진 수 (장)", 0, 300, default_ph)
        st.session_state.my_photos = my_photos

        default_mn = int(st.session_state.my_min_nights) if st.session_state.my_min_nights is not None else int(bench_val(bench, "min_nights", 2))
        my_min_nights = st.number_input(
            "최소 숙박일 (박)",
            1, 365, default_mn,
            help="게스트가 예약할 수 있는 최소 숙박 기간",
        )
        st.session_state.my_min_nights = my_min_nights

        st.markdown("**📍 위치 정보**")
        default_poi = float(st.session_state.my_poi_dist) if st.session_state.my_poi_dist is not None else round(bench_val(bench, "nearest_poi_dist_km", 0.10), 2)
        my_poi_dist = st.number_input("가장 가까운 관광지까지 거리 (km)", 0.0, 5.0, default_poi, 0.01)
        st.session_state.my_poi_dist = my_poi_dist

        default_500 = int(st.session_state.my_500m) if st.session_state.my_500m is not None else int(bench_val(bench, "nearest_500m", 19))
        my_500m = st.number_input("도보 10분(500m) 이내 관광지 수", 0, 300, default_500)
        st.session_state.my_500m = my_500m

        poi_idx = POI_TYPES.index(st.session_state.my_poi_type) if st.session_state.my_poi_type in POI_TYPES else 0
        my_poi_type = st.selectbox("가장 가까운 관광지 유형", POI_TYPES, index=poi_idx)
        st.session_state.my_poi_type = my_poi_type

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("← 이전", key="back4", use_container_width=True):
            st.session_state.step = 3
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        if st.button("🔍 분석 결과 보기", key="next4", use_container_width=True):
            st.session_state.step = 5
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 5 — 결과 대시보드
# ═══════════════════════════════════════════════════════════════════════════════
def step5():
    # ── 값 수집 ─────────────────────────────────────────────────────────────
    district      = st.session_state.district
    room_type     = st.session_state.room_type
    my_adr        = float(st.session_state.my_adr or 100000)
    my_occ        = (st.session_state.my_occ_pct or 40) / 100
    my_photos     = int(st.session_state.my_photos or 20)
    my_superhost  = bool(st.session_state.my_superhost)
    my_instant    = bool(st.session_state.my_instant)
    my_extra_fee  = bool(st.session_state.my_extra_fee)
    my_min_nights = int(st.session_state.my_min_nights or 2)
    my_rating     = float(st.session_state.my_rating or 4.7)
    my_reviews    = int(st.session_state.my_reviews or 10)
    my_poi_dist   = float(st.session_state.my_poi_dist or 0.3)
    my_bedrooms   = int(st.session_state.get("my_bedrooms") or 1)
    my_baths      = float(st.session_state.get("my_baths") or 1.0)
    my_guests     = int(st.session_state.get("my_guests") or 2)
    opex_items = {
        "전기세": st.session_state.opex_elec,
        "수도세": st.session_state.opex_water,
        "관리비": st.session_state.opex_mgmt,
        "인터넷": st.session_state.opex_net,
        "청소비": st.session_state.opex_clean,
        "대출이자": st.session_state.opex_loan,
        "기타": st.session_state.opex_etc,
    }
    total_opex = sum(opex_items.values())

    # ── ML 모델 실행 ─────────────────────────────────────────────────────────
    _ml_artifacts = load_ml_models()
    _dist_stats   = compute_district_stats(active_df, cluster_df)
    ml_result = None
    ml_error  = None
    if _ml_artifacts is not None:
        try:
            _features = build_listing_features(st.session_state, _dist_stats)
            from predict_utils import predict_revpar
            ml_result = predict_revpar(_features, total_opex, **_ml_artifacts)
        except Exception as _e:
            ml_error = str(_e)

    bench     = get_bench(district, room_type)
    b_adr     = bench_val(bench, "ttm_avg_rate", 100000)
    b_adr_p25 = bench_val(bench, "ttm_avg_rate", 70000, 25)
    b_adr_p75 = bench_val(bench, "ttm_avg_rate", 140000, 75)
    b_revpar  = bench_val(bench, "ttm_revpar", 40000)

    my_revpar       = my_adr * my_occ
    monthly_revenue = my_revpar * 30
    airbnb_fee      = monthly_revenue * 0.03
    net_profit      = monthly_revenue - airbnb_fee - total_opex
    bep_adr         = (total_opex / 0.97) / (30 * my_occ) if my_occ > 0 else 0

    d_row = cluster_df[cluster_df["district"] == district]
    cluster_name = d_row["cluster_name"].values[0] if len(d_row) > 0 else "가성비 신흥형"
    c_info     = CLUSTER_INFO.get(cluster_name, CLUSTER_INFO["가성비 신흥형"])
    elasticity = c_info["elasticity"]
    d_name     = dn(district)
    rt_name    = ROOM_TYPE_KR.get(room_type, room_type)

    # ── 헤더 ────────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="text-align:center;padding:28px 0 8px;">
      <div style="font-size:30px;margin-bottom:10px;">🏠</div>
      <h2 style="color:#FF5A5F;margin:0 0 6px;font-weight:800;letter-spacing:-0.6px;font-size:26px;">분석 결과</h2>
      <p style="color:#9CA3AF;font-size:13px;margin:0;font-weight:400;">
        {d_name} · {rt_name} · 실운영 숙소 {len(bench):,}개 기준
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── 섹션 A: 요약 지표 ───────────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    k1, k2, k3 = st.columns(3)

    revpar_diff  = my_revpar - b_revpar
    profit_color = "#2E7D32" if net_profit > 0 else "#C62828"
    bep_ok       = my_adr >= bep_adr

    def kpi_card(col, label, value, sub, sub_color="#767676"):
        col.markdown(
            f'<div style="background:white;border-radius:12px;padding:18px;text-align:center;'
            f'box-shadow:0 2px 10px rgba(0,0,0,0.06);">'
            f'<div style="font-size:12px;color:#888;margin-bottom:6px;">{label}</div>'
            f'<div style="font-size:24px;font-weight:700;color:#484848;">{value}</div>'
            f'<div style="font-size:12px;color:{sub_color};margin-top:4px;">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    kpi_card(k1, "내 하루 평균 실수익", f"₩{int(my_revpar):,}",
             f"지역 평균 대비 {'▲' if revpar_diff >= 0 else '▼'}₩{int(abs(revpar_diff)):,}",
             "#2E7D32" if revpar_diff >= 0 else "#C62828")
    kpi_card(k2, "월 예상 순이익", f"₩{int(net_profit):,}",
             "흑자 ✅" if net_profit > 0 else "적자 ❌", profit_color)
    kpi_card(k3, "본전 요금 (손해 없는 최소 요금)", f"₩{int(bep_adr):,}",
             f"현재 요금 {'위 ✅' if bep_ok else '아래 ❌'}",
             "#2E7D32" if bep_ok else "#C62828")

    # ── 섹션 A': ML 진단 ────────────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    section_title("🤖 ML 시장 진단", "머신러닝 모델이 유사 숙소 데이터를 기반으로 산출한 시장 적정 지표입니다.")

    if ml_error:
        st.info("ML 모델 로드 실패 — 공식 기반 분석으로 대체합니다.")
    elif ml_result is None:
        st.info("ML 모델 로드 실패 — 공식 기반 분석으로 대체합니다.")
    else:
        adr_pred   = ml_result["ADR_pred"]
        occ_pred   = ml_result["Occ_pred"]
        revp_pred  = ml_result["RevPAR_pred"]
        price_gap  = my_adr - adr_pred
        occ_gap    = my_occ - occ_pred

        ml1, ml2, ml3 = st.columns(3)

        def ml_card(col, label, pred_val, user_val, fmt_pred, fmt_gap, gap_val, unit=""):
            gap_abs = abs(gap_val)
            if gap_val > 0:
                direction, gap_color = "▲", "#C62828"
                gap_text = f"시장 적정보다 {fmt_gap.format(gap_abs)} 높음"
            elif gap_val < 0:
                direction, gap_color = "▼", "#2E7D32"
                gap_text = f"시장 적정보다 {fmt_gap.format(gap_abs)} 낮음"
            else:
                direction, gap_color, gap_text = "─", "#767676", "시장 적정 수준"
            col.markdown(
                f'<div style="background:white;border-radius:12px;padding:18px;text-align:center;'
                f'box-shadow:0 2px 10px rgba(0,0,0,0.06);">'
                f'<div style="font-size:12px;color:#888;margin-bottom:4px;">{label}</div>'
                f'<div style="font-size:22px;font-weight:700;color:#484848;">{fmt_pred.format(pred_val)}</div>'
                f'<div style="font-size:11px;color:{gap_color};margin-top:4px;">{direction} {gap_text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        ml_card(ml1, "시장 적정 ADR",
                adr_pred, my_adr,
                "₩{:,.0f}", "₩{:,.0f}", price_gap)
        ml_card(ml2, "ML 예측 예약률",
                occ_pred, my_occ,
                "{:.1%}", "{:.1%}", occ_gap)
        ml_card(ml3, "ML 예측 RevPAR",
                revp_pred, my_revpar,
                "₩{:,.0f}", "₩{:,.0f}", my_revpar - revp_pred)

        # 가격 갭 해석 박스
        gap_pct = (price_gap / adr_pred * 100) if adr_pred > 0 else 0
        if gap_pct > 10:
            gap_msg = f"현재 요금이 시장 적정 요금보다 {gap_pct:.0f}% 높습니다 → 예약률이 눌릴 수 있어요."
            gap_bg, gap_border = "#FFF8E1", "#FFB400"
        elif gap_pct < -10:
            gap_msg = f"현재 요금이 시장 적정 요금보다 {abs(gap_pct):.0f}% 낮습니다 → 요금 인상 여력이 있습니다."
            gap_bg, gap_border = "#E8F5E9", "#66BB6A"
        else:
            gap_msg = f"현재 요금({gap_pct:+.0f}%)이 시장 적정 구간 안에 있습니다."
            gap_bg, gap_border = "#F3F4F6", "#9CA3AF"

        st.markdown(
            f'<div style="background:{gap_bg};border-left:4px solid {gap_border};border-radius:10px;'
            f'padding:14px 18px;margin-top:10px;">'
            f'<div style="font-size:13px;color:#484848;">💡 {gap_msg}</div>'
            f'<div style="font-size:11px;color:#AAAAAA;margin-top:6px;">'
            f'Model A (LightGBM ADR) · Model B (LightGBM Occupancy) · Isotonic RevPAR 보정</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── 섹션 B: 적정 요금 추천 ──────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    section_title("💡 내 숙소에 맞는 적정 요금", "내 운영 단계에 따라 추천 요금 구간이 달라집니다.")

    if my_superhost and my_rating >= 4.8 and my_reviews >= 50:
        stage, s_color, s_icon = "프리미엄", "#FF5A5F", "🏆"
        rec_min, rec_max = int(b_adr), int(b_adr_p75)
        s_tip = "현재 요금이 지역 평균보다 낮다면 10~20% 인상을 테스트해보세요."
    elif my_reviews >= 10 and my_rating >= 4.5:
        stage, s_color, s_icon = "안정", "#00A699", "📈"
        rec_min, rec_max = int(b_adr_p25), int(b_adr)
        s_tip = "슈퍼호스트 달성 후 요금을 지역 평균 이상으로 올릴 수 있습니다."
    else:
        stage, s_color, s_icon = "신규", "#2196F3", "🌱"
        rec_min = max(int(bep_adr), int(b_adr_p25 * 0.85))
        rec_max = int(b_adr_p25)
        s_tip = "하위 25% 요금으로 첫 10건의 리뷰를 빠르게 쌓은 후 요금을 올리세요."

    t1, t2, t3 = st.columns(3)
    stage_data = [
        ("신규", "🌱", "#2196F3", f"₩{int(b_adr_p25*0.85):,} ~ ₩{int(b_adr_p25):,}", "리뷰 10건 미만"),
        ("안정", "📈", "#00A699", f"₩{int(b_adr_p25):,} ~ ₩{int(b_adr):,}", "리뷰 10건+ & 평점 4.5+"),
        ("프리미엄", "🏆", "#FF5A5F", f"₩{int(b_adr):,} ~ ₩{int(b_adr_p75):,}", "슈퍼호스트 & 평점 4.8+"),
    ]
    for col, (sname, sicon, scolor, sprice, scond) in zip([t1, t2, t3], stage_data):
        is_me = sname == stage
        bg     = scolor if is_me else "#F7F7F7"
        fc     = "white" if is_me else "#767676"
        border = f"3px solid {scolor}" if is_me else "2px solid #EBEBEB"
        me_tag = (f'<div style="margin-top:8px;"><span style="background:white;color:{scolor};'
                  f'padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700;">▲ 내 단계</span></div>'
                  if is_me else "")
        col.markdown(
            f'<div style="border:{border};border-radius:12px;padding:18px;text-align:center;background:{bg};color:{fc};">'
            f'<div style="font-size:24px;">{sicon}</div>'
            f'<div style="font-weight:700;font-size:14px;margin:6px 0;">{sname} 호스트</div>'
            f'<div style="font-size:11px;opacity:0.85;margin-bottom:10px;">{scond}</div>'
            f'<div style="font-size:16px;font-weight:700;">{sprice}</div>'
            f'{me_tag}'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if my_adr < rec_min:
        gap_msg, gap_icon, gap_bg = (f"현재 요금 ₩{int(my_adr):,}이 추천 구간보다 ₩{rec_min - int(my_adr):,} 낮습니다. 조금 올려도 괜찮습니다.", "⬆️", "#E3F2FD")
    elif my_adr > rec_max:
        gap_msg, gap_icon, gap_bg = (f"현재 요금 ₩{int(my_adr):,}이 추천 구간보다 ₩{int(my_adr) - rec_max:,} 높습니다. 예약률이 낮다면 조정을 고려하세요.", "⚠️", "#FFF8E1")
    else:
        gap_msg, gap_icon, gap_bg = ("현재 요금이 내 단계에 맞는 구간 안에 있습니다. 잘 하고 계세요!", "✅", "#E8F5E9")

    st.markdown(
        f'<div style="background:{gap_bg};border-left:4px solid {s_color};border-radius:10px;padding:16px 18px;">'
        f'<div style="font-weight:700;color:{s_color};margin-bottom:6px;">{s_icon} 내 단계: {stage} 호스트 — 추천 요금 ₩{rec_min:,} ~ ₩{rec_max:,}</div>'
        f'<div style="font-size:13px;color:#484848;">{gap_icon} {gap_msg}</div>'
        f'<div style="font-size:12px;color:#767676;margin-top:6px;">💬 {s_tip}</div>'
        f'<div style="font-size:11px;color:#AAAAAA;margin-top:8px;">'
        f'본전 요금 ₩{int(bep_adr):,} | 지역 하위25% ₩{int(b_adr_p25):,} | 지역 평균 ₩{int(b_adr):,} | 지역 상위25% ₩{int(b_adr_p75):,}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── 섹션 C: 월 손익 계산서 ──────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    section_title("💰 월 손익 계산서", "이번 달 예상 수익 구조입니다.")

    col_pnl, col_pie = st.columns(2)

    with col_pnl:
        rows = [
            ("월 매출", f"₩{int(monthly_revenue):,}", "#484848"),
            ("에어비앤비 수수료 (3%)", f"- ₩{int(airbnb_fee):,}", "#C62828"),
            ("월 운영비", f"- ₩{int(total_opex):,}", "#C62828"),
        ]
        html = '<div style="background:white;border-radius:12px;padding:20px;box-shadow:0 2px 10px rgba(0,0,0,0.06);">'
        for label, value, color in rows:
            html += (f'<div style="display:flex;justify-content:space-between;padding:9px 0;'
                     f'border-bottom:1px solid #F5F5F5;">'
                     f'<span style="color:#767676;font-size:14px;">{label}</span>'
                     f'<span style="color:{color};font-weight:600;">{value}</span></div>')
        profit_color2 = "#2E7D32" if net_profit >= 0 else "#C62828"
        html += (f'<div style="display:flex;justify-content:space-between;padding:12px 0 0;">'
                 f'<span style="font-weight:700;font-size:15px;">월 순이익</span>'
                 f'<span style="font-weight:700;font-size:18px;color:{profit_color2};">₩{int(net_profit):,}</span></div>')
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

        if net_profit > 0:
            st.success(f"✅ 월 ₩{int(net_profit):,} 흑자입니다.")
        elif net_profit == 0:
            st.warning("⚠️ 정확히 본전 상태입니다.")
        else:
            st.error(f"❌ 월 ₩{int(abs(net_profit)):,} 적자입니다. 요금 인상 또는 운영비 절감이 필요합니다.")

    with col_pie:
        nonzero = {k: v for k, v in opex_items.items() if v > 0}
        if nonzero and total_opex > 0:
            fig, ax = plt.subplots(figsize=(4.5, 4))
            colors = ["#FF5A5F", "#FF8A8D", "#FFB3B5", "#00A699", "#4DB6AC", "#FFB400", "#EBEBEB"]
            ax.pie(
                nonzero.values(), labels=nonzero.keys(),
                autopct="%1.0f%%", startangle=90,
                colors=colors[:len(nonzero)],
                textprops={"fontsize": 10},
                wedgeprops={"linewidth": 1, "edgecolor": "white"},
            )
            ax.set_title(f"월 운영비 구성 (총 ₩{total_opex:,})", fontsize=11)
            fig.patch.set_facecolor("#FAFAFA")
            fig.tight_layout()
            st.pyplot(fig)
            plt.close()
        else:
            st.info("운영비를 입력하면 구성 차트가 표시됩니다.")

    # ── 섹션 D: 운영 체크리스트 ─────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    section_title("🗒️ 지금 바로 개선할 수 있는 것들")

    checks = []

    if my_superhost:
        checks.append(("✅", "슈퍼호스트 달성", "수익 +83% 프리미엄 유지 중", "done"))
    else:
        est = my_revpar * 1.831
        checks.append(("🔴", "슈퍼호스트 미달성",
            f"달성 시 하루 수익 ₩{int(my_revpar):,} → ₩{int(est):,} 잠재", "todo"))

    if my_instant:
        checks.append(("✅", "즉시예약 켜짐", "예약률 최대화 중", "done"))
    else:
        checks.append(("🟡", "즉시예약 꺼짐", "설정 1분, 비용 없음 → 예약률 +5~10% 기대", "quick"))

    if 20 <= my_photos <= 35:
        checks.append(("✅", f"사진 {my_photos}장 (최적)", "최적 20~35장 구간 유지 중", "done"))
    elif my_photos < 20:
        checks.append(("🔴", f"사진 {my_photos}장 (부족)", f"{20 - my_photos}장 추가 → 클릭률 상승 구간 진입", "todo"))
    else:
        checks.append(("🟡", f"사진 {my_photos}장 (많음)", "35장 초과 — 좋은 사진만 추려서 정리 권장", "quick"))

    if not my_extra_fee:
        checks.append(("✅", "추가 게스트 요금 없음", "요금에 포함 — 최적 구조", "done"))
    else:
        checks.append(("🔴", "추가 게스트 요금 있음",
            "없애고 1박 요금에 통합 → 수익 +25~56% 회복 가능", "quick"))

    if 2 <= my_min_nights <= 3:
        checks.append(("✅", f"최소 {my_min_nights}박 (최적)", "수익 최적 + 리뷰 축적 속도 최적", "done"))
    elif my_min_nights == 1:
        checks.append(("🟡", "최소 1박", "수익 효율 낮음 — 2박으로 변경 추천", "quick"))
    else:
        checks.append(("🟡", f"최소 {my_min_nights}박 (길음)", "리뷰 쌓는 속도 느림 — 2~3박으로 줄이기 검토", "quick"))

    if my_rating >= 4.8:
        checks.append(("✅", f"평점 {my_rating:.1f}", "슈퍼호스트 기준 충족 + 검색 상위 노출 구간", "done"))
    elif my_rating >= 4.5:
        checks.append(("🟡", f"평점 {my_rating:.1f}", "4.8 이상이면 슈퍼호스트 + 검색 부스트", "todo"))
    else:
        checks.append(("🔴", f"평점 {my_rating:.1f} (낮음)", "4.5 미만 — 검색 노출 불이익 구간", "todo"))

    if my_reviews >= 10:
        checks.append(("✅", f"리뷰 {my_reviews}건", "슈퍼호스트 최소 요건(10건) 충족", "done"))
    else:
        checks.append(("🔴", f"리뷰 {my_reviews}건",
            f"슈퍼호스트 최소 10건 필요 — {10 - my_reviews}건 더 받아야 합니다", "todo"))

    # 우선순위 분류 (urgent → quick → done)
    checks_todo  = [(ic, t, d, s) for ic, t, d, s in checks if s == "todo"]
    checks_quick = [(ic, t, d, s) for ic, t, d, s in checks if s == "quick"]
    checks_done  = [(ic, t, d, s) for ic, t, d, s in checks if s == "done"]
    action_items = checks_todo + checks_quick
    n_action = len(action_items)
    n_done   = len(checks_done)

    # 요약 배너
    if n_action == 0:
        st.markdown(
            '<div style="background:#E8F5E9;border:1.5px solid #66BB6A;border-radius:12px;'
            'padding:16px 20px;margin-bottom:20px;">'
            '<div style="font-size:16px;font-weight:700;color:#2E7D32;">🎉 모든 운영 레버가 최적 상태입니다!</div>'
            '<div style="font-size:13px;color:#555;margin-top:4px;">지금 이대로 수익 최대화 상태를 유지하고 있어요.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f'<div style="background:#FFF5F5;border:1.5px solid #FF5A5F;border-radius:12px;'
            f'padding:16px 20px;margin-bottom:20px;display:flex;align-items:center;gap:16px;">'
            f'<div style="font-size:32px;">🎯</div>'
            f'<div>'
            f'<div style="font-size:16px;font-weight:700;color:#C62828;">'
            f'{n_action}개 항목을 개선하면 수익을 더 높일 수 있어요</div>'
            f'<div style="font-size:13px;color:#717171;margin-top:3px;">'
            f'우선순위 순으로 개선해 보세요 · {n_done}개 항목은 이미 최적 상태</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    def _check_card(col, icon, title, desc, status):
        if status == "done":
            bg, border, title_c = "#F0FAF4", "#66BB6A", "#2E7D32"
            badge = ('<span style="display:inline-block;background:#E8F5E9;color:#2E7D32;'
                     'padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-top:8px;">✓ 최적</span>')
        elif status == "todo":
            bg, border, title_c = "#FFF0EF", "#FF5A5F", "#C62828"
            badge = ('<span style="display:inline-block;background:#FFEBEE;color:#C62828;'
                     'padding:2px 10px;border-radius:20px;font-size:11px;font-weight:700;margin-top:8px;">⚠ 개선 필요</span>')
        else:  # quick
            bg, border, title_c = "#FFFCF0", "#FFB400", "#B45309"
            badge = ('<span style="display:inline-block;background:#FFF8E1;color:#B45309;'
                     'padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;margin-top:8px;">💡 빠른 수정</span>')
        col.markdown(
            f'<div style="background:{bg};border-left:4px solid {border};border-radius:10px;'
            f'padding:14px 16px;margin-bottom:10px;">'
            f'<div style="font-weight:700;font-size:14px;color:{title_c};">{icon} {title}</div>'
            f'<div style="font-size:12px;color:#555;margin-top:5px;line-height:1.55;">{desc}</div>'
            f'{badge}'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ① 개선이 필요한 항목 먼저
    if action_items:
        st.markdown(
            '<div style="font-size:12px;font-weight:700;color:#C62828;letter-spacing:0.8px;'
            'text-transform:uppercase;margin-bottom:10px;">📌 개선이 필요한 항목</div>',
            unsafe_allow_html=True,
        )
        for idx in range(0, len(action_items), 2):
            cols = st.columns(2)
            for j, item in enumerate(action_items[idx:idx + 2]):
                _check_card(cols[j], *item)

    # ② 이미 최적인 항목
    if checks_done:
        st.markdown(
            '<div style="font-size:12px;font-weight:700;color:#2E7D32;letter-spacing:0.8px;'
            'text-transform:uppercase;margin:16px 0 10px;">✅ 이미 잘 하고 있는 것들</div>',
            unsafe_allow_html=True,
        )
        for idx in range(0, len(checks_done), 2):
            cols = st.columns(2)
            for j, item in enumerate(checks_done[idx:idx + 2]):
                _check_card(cols[j], *item)

    # ③ 즉시 실행 액션 TOP 3
    if action_items:
        st.markdown(
            '<div style="font-size:18px;font-weight:700;color:#222;margin:28px 0 12px;">'
            '🎯 지금 당장 실행하면 효과 큰 TOP 3</div>',
            unsafe_allow_html=True,
        )
        priority_colors = ["#FF5A5F", "#FF8C00", "#2196F3"]
        for i, (icon, title, desc, _) in enumerate(action_items[:3], 1):
            pc = priority_colors[i - 1]
            st.markdown(
                f'<div style="background:white;border:1px solid #EBEBEB;border-radius:12px;'
                f'padding:16px 18px;margin-bottom:8px;display:flex;align-items:flex-start;'
                f'box-shadow:0 2px 8px rgba(0,0,0,0.05);">'
                f'<div style="background:{pc};color:white;border-radius:50%;min-width:28px;height:28px;'
                f'display:flex;align-items:center;justify-content:center;font-size:13px;'
                f'font-weight:700;margin-right:14px;flex-shrink:0;">{i}</div>'
                f'<div>'
                f'<div style="font-weight:700;font-size:15px;color:#222;">{icon} {title}</div>'
                f'<div style="font-size:13px;color:#717171;margin-top:4px;">{desc}</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── 섹션 D': 헬스 스코어 ────────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    section_title("💊 숙소 헬스 스코어", "클러스터 내 유사 숙소와 비교한 5가지 운영 건강도 지표입니다.")

    _cluster_id = _dist_stats.get(district, {}).get("cluster", 2)
    _cluster_listings = active_df[active_df["cluster"] == _cluster_id].copy()

    _user_vals = {
        "my_reviews":    my_reviews,
        "my_rating":     my_rating,
        "my_photos":     my_photos,
        "my_instant":    my_instant,
        "my_min_nights": my_min_nights,
        "my_extra_fee":  my_extra_fee,
        "my_poi_dist":   my_poi_dist,
        "my_bedrooms":   my_bedrooms,
        "my_baths":      my_baths,
    }
    _hs = compute_health_score(_user_vals, _cluster_listings)
    _score     = _hs["composite"]
    _grade     = _hs["grade"]
    _comps     = _hs["components"]
    _grade_colors = {"A": "#2E7D32", "B": "#00A699", "C": "#FFB400", "D": "#FF8C00", "F": "#C62828"}
    _gc = _grade_colors.get(_grade, "#767676")

    hs_left, hs_right = st.columns([1, 1.6])

    with hs_left:
        st.markdown(
            f'<div style="background:{_gc}18;border:2.5px solid {_gc};border-radius:16px;'
            f'padding:28px 20px;text-align:center;">'
            f'<div style="font-size:52px;font-weight:800;color:{_gc};">{int(_score)}</div>'
            f'<div style="font-size:13px;color:#767676;margin-top:2px;">/ 100</div>'
            f'<div style="background:{_gc};color:white;border-radius:50%;width:48px;height:48px;'
            f'display:inline-flex;align-items:center;justify-content:center;'
            f'font-size:22px;font-weight:800;margin-top:12px;">{_grade}</div>'
            f'<div style="font-size:12px;color:#767676;margin-top:8px;">클러스터 내 백분위 기준</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with hs_right:
        _comp_labels = {
            "review_signal":   "리뷰 신호",
            "listing_quality": "사진 품질",
            "booking_policy":  "예약 정책",
            "location":        "위치",
            "listing_config":  "숙소 구성",
        }
        _bar_html = ""
        for key, label in _comp_labels.items():
            v = _comps[key]
            bar_color = "#2E7D32" if v >= 70 else "#FFB400" if v >= 40 else "#C62828"
            _bar_html += (
                f'<div style="margin-bottom:10px;">'
                f'<div style="display:flex;justify-content:space-between;'
                f'font-size:13px;margin-bottom:4px;">'
                f'<span style="color:#484848;">{label}</span>'
                f'<span style="font-weight:600;color:{bar_color};">{int(v)}/100</span></div>'
                f'<div style="background:#EBEBEB;border-radius:6px;height:8px;">'
                f'<div style="background:{bar_color};width:{v:.0f}%;height:8px;'
                f'border-radius:6px;transition:width 0.3s;"></div></div></div>'
            )
        st.markdown(_bar_html, unsafe_allow_html=True)

        # 약한 컴포넌트 액션
        _actions = []
        if _comps["review_signal"] < 40:
            _actions.append("📝 리뷰 수집 강화 — 게스트에게 리뷰 요청 메시지 발송")
        if _comps["booking_policy"] < 40:
            _actions.append("⚡ 즉시예약 활성화 또는 최소박 단축 검토")
        if _comps["listing_quality"] < 40:
            _actions.append("📸 사진 21~35장 최적 구간으로 보정")
        if _comps["listing_config"] < 30:
            _actions.append("🛏️ 침실·욕실 정보 정확도 검토")
        if _comps["location"] < 30:
            _actions.append("📍 근처 POI 설명 보강 — 위치 어필 강화")

        if _actions:
            actions_html = '<div style="margin-top:8px;background:#FFF5F5;border-radius:8px;padding:12px 14px;">'
            actions_html += '<div style="font-size:11px;font-weight:700;color:#C62828;margin-bottom:6px;">개선 액션</div>'
            for a in _actions:
                actions_html += f'<div style="font-size:12px;color:#484848;margin-bottom:4px;">{a}</div>'
            actions_html += "</div>"
            st.markdown(actions_html, unsafe_allow_html=True)

    # ── 섹션 E: 요금 시뮬레이션 ────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    section_title(
        "📊 요금 변경 시뮬레이션",
        f"이 지역({cluster_name})은 요금을 10% 올리면 예약률이 약 {abs(elasticity)*10:.0f}% 변화합니다.",
    )

    delta_pct = st.slider("요금 변화율 (%)", -30, 50, 0, 5,
                          help="오른쪽: 요금 인상 / 왼쪽: 요금 인하")
    delta    = delta_pct / 100
    new_adr  = my_adr * (1 + delta)
    new_occ  = min(1.0, max(0.0, my_occ * (1 + elasticity * delta)))
    new_revp = new_adr * new_occ
    new_net  = new_revp * 30 * 0.97 - total_opex
    p_change = new_net - net_profit

    col_s1, col_s2 = st.columns(2)

    with col_s1:
        sim_rows = [
            ("1박 요금", f"₩{int(my_adr):,}", f"₩{int(new_adr):,}", f"{delta_pct:+d}%"),
            ("예약률", f"{my_occ:.0%}", f"{new_occ:.0%}", f"{(new_occ-my_occ)*100:+.1f}%p"),
            ("하루 실수익", f"₩{int(my_revpar):,}", f"₩{int(new_revp):,}",
             f"{(new_revp/my_revpar-1)*100:+.1f}%" if my_revpar > 0 else "-"),
            ("월 순이익", f"₩{int(net_profit):,}", f"₩{int(new_net):,}", f"₩{p_change:+,.0f}"),
        ]
        html = ('<div style="background:white;border-radius:12px;padding:20px;'
                'box-shadow:0 2px 10px rgba(0,0,0,0.06);">'
                '<div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;'
                'color:#888;font-size:12px;font-weight:600;padding-bottom:8px;'
                'border-bottom:1.5px solid #F0F0F0;margin-bottom:4px;">'
                '<span>항목</span><span style="text-align:right;">현재</span>'
                '<span style="text-align:right;">변경 후</span>'
                '<span style="text-align:right;">변화</span></div>')
        for label, cur, nxt, chg in sim_rows:
            w = "700" if "순이익" in label else "400"
            chg_c = "#2E7D32" if ("+" in chg and "₩-" not in chg) else "#C62828" if ("-" in chg and "₩+" not in chg) else "#484848"
            html += (f'<div style="display:grid;grid-template-columns:2fr 1fr 1fr 1fr;'
                     f'padding:9px 0;border-bottom:1px solid #F5F5F5;font-weight:{w};">'
                     f'<span style="font-size:13px;">{label}</span>'
                     f'<span style="text-align:right;font-size:13px;">{cur}</span>'
                     f'<span style="text-align:right;font-size:13px;">{nxt}</span>'
                     f'<span style="text-align:right;font-size:13px;color:{chg_c};">{chg}</span></div>')
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

        if delta_pct == 0:
            st.info("슬라이더를 움직여 요금 변화 효과를 확인하세요.")
        elif delta_pct > 0 and p_change > 0:
            st.success(f"✅ 요금 인상 효과 있음 — 순이익 ₩{p_change:+,.0f} 증가")
        elif delta_pct > 0:
            st.error(f"❌ 요금 인상이 역효과 — 예약률 하락으로 순이익 ₩{abs(p_change):,.0f} 감소")
        elif p_change > 0:
            st.success(f"✅ 요금 인하로 예약률 상승 → 순이익 ₩{p_change:+,.0f} 증가")
        else:
            st.warning(f"⚠️ 요금 인하 시 순이익 ₩{abs(p_change):,.0f} 감소")

    with col_s2:
        x_range = np.linspace(-0.30, 0.50, 80)
        profits = [
            my_adr*(1+d) * min(1., max(0., my_occ*(1+elasticity*d))) * 30 * 0.97 - total_opex
            for d in x_range
        ]
        fig4, ax4 = plt.subplots(figsize=(5.5, 4))
        ax4.plot(x_range * 100, profits, color="#FF5A5F", linewidth=2.5)
        ax4.axhline(0, color="#767676", linestyle="--", lw=1.2, alpha=0.6, label="손익분기선")
        ax4.axvline(delta_pct, color="#FFB400", linestyle="--", lw=1.5, label=f"현재 ({delta_pct:+d}%)")
        ax4.scatter([delta_pct], [new_net], color="#FFB400", s=70, zorder=6)
        ax4.fill_between(x_range*100, profits, 0, where=[p > 0 for p in profits], alpha=0.07, color="#4CAF50")
        ax4.fill_between(x_range*100, profits, 0, where=[p <= 0 for p in profits], alpha=0.07, color="#FF5A5F")
        ax4.set_xlabel("요금 변화율 (%)")
        ax4.set_ylabel("월 순이익 (원)")
        ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"₩{y/10000:.0f}만"))
        ax4.legend(fontsize=8)
        ax4.spines["top"].set_visible(False)
        ax4.spines["right"].set_visible(False)
        ax4.set_facecolor("#FAFAFA")
        fig4.patch.set_facecolor("#FAFAFA")
        fig4.tight_layout()
        st.pyplot(fig4)
        plt.close()

        best_idx  = int(np.argmax(profits))
        best_adr  = my_adr * (1 + x_range[best_idx])
        best_prof = profits[best_idx]
        st.success(f"🎯 순이익 최대 요금: ₩{int(best_adr):,} ({x_range[best_idx]*100:+.0f}%) → 월 ₩{int(best_prof):,}")

    # ── 섹션 F': 포지셔닝 매트릭스 + 시장 유형 ─────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    section_title("📍 클러스터 포지셔닝 매트릭스", "같은 시장 유형 내 숙소 대비 내 위치입니다.")

    # ── 사분면 산점도 ───────────────────────────────────────────────────────
    _cl = _cluster_listings.copy()
    _adr_vals = _cl["ttm_avg_rate"].dropna()
    _occ_vals = _cl["ttm_occupancy"].dropna()

    if len(_adr_vals) > 5 and len(_occ_vals) > 5:
        _cl["adr_pct"] = _cl["ttm_avg_rate"].apply(
            lambda x: float(np.mean(_adr_vals <= x) * 100) if not pd.isna(x) else 50.0
        )
        _cl["occ_pct"] = _cl["ttm_occupancy"].apply(
            lambda x: float(np.mean(_occ_vals <= x) * 100) if not pd.isna(x) else 50.0
        )
        user_adr_pct = float(np.mean(_adr_vals <= my_adr) * 100)
        user_occ_pct = float(np.mean(_occ_vals <= my_occ) * 100)

        _qcols = st.columns([1, 1])
        with _qcols[0]:
            fig_q, ax_q = plt.subplots(figsize=(5, 5))
            # 사분면 배경
            ax_q.axhspan(50, 100, xmin=0,   xmax=0.5, alpha=0.06, color="#FFB400")   # 물량형
            ax_q.axhspan(50, 100, xmin=0.5, xmax=1.0, alpha=0.06, color="#2E7D32")   # 고수익형
            ax_q.axhspan(0,  50,  xmin=0,   xmax=0.5, alpha=0.06, color="#C62828")   # 침체형
            ax_q.axhspan(0,  50,  xmin=0.5, xmax=1.0, alpha=0.06, color="#FF8C00")   # 고가위험형
            ax_q.axhline(50, color="#CCCCCC", lw=1, ls="--")
            ax_q.axvline(50, color="#CCCCCC", lw=1, ls="--")
            # 사분면 레이블
            ax_q.text(25, 75, "물량형",   ha="center", va="center", fontsize=9, color="#B45309", alpha=0.7)
            ax_q.text(75, 75, "고수익형", ha="center", va="center", fontsize=9, color="#1B5E20", alpha=0.7)
            ax_q.text(25, 25, "침체형",   ha="center", va="center", fontsize=9, color="#B71C1C", alpha=0.7)
            ax_q.text(75, 25, "고가위험형", ha="center", va="center", fontsize=9, color="#E65100", alpha=0.7)
            # 클러스터 전체 산점도
            ax_q.scatter(
                _cl["adr_pct"].dropna(), _cl["occ_pct"].dropna(),
                s=15, alpha=0.18, color="#9CA3AF", zorder=2,
            )
            # 내 숙소
            ax_q.scatter(
                [user_adr_pct], [user_occ_pct],
                s=200, marker="*", color="#FF5A5F", zorder=5, label="내 숙소",
            )
            ax_q.annotate(
                "내 숙소",
                (user_adr_pct, user_occ_pct),
                textcoords="offset points", xytext=(8, 6),
                fontsize=9, color="#FF5A5F", fontweight="bold",
            )
            ax_q.set_xlim(0, 100)
            ax_q.set_ylim(0, 100)
            ax_q.set_xlabel("ADR 분위 (클러스터 내, %)", fontsize=9)
            ax_q.set_ylabel("예약률 분위 (클러스터 내, %)", fontsize=9)
            ax_q.set_title(f"{cluster_name} 포지셔닝", fontsize=10, fontweight="bold")
            ax_q.spines["top"].set_visible(False)
            ax_q.spines["right"].set_visible(False)
            ax_q.set_facecolor("#FAFAFA")
            fig_q.patch.set_facecolor("#FAFAFA")
            fig_q.tight_layout()
            st.pyplot(fig_q)
            plt.close()

            # 사분면 위치 텍스트
            if user_adr_pct >= 50 and user_occ_pct >= 50:
                q_label, q_color = "고수익형 — ADR·예약률 모두 상위", "#2E7D32"
            elif user_adr_pct >= 50 and user_occ_pct < 50:
                q_label, q_color = "고가위험형 — 요금은 높지만 예약률이 낮음", "#E65100"
            elif user_adr_pct < 50 and user_occ_pct >= 50:
                q_label, q_color = "물량형 — 예약률은 높지만 요금이 낮음", "#B45309"
            else:
                q_label, q_color = "침체형 — ADR·예약률 모두 하위", "#B71C1C"
            st.markdown(
                f'<div style="background:{q_color}12;border-left:4px solid {q_color};'
                f'border-radius:8px;padding:10px 14px;font-size:13px;font-weight:600;color:{q_color};">'
                f'📌 {q_label}</div>',
                unsafe_allow_html=True,
            )
    # (else: not enough data — quadrant skipped)

    # ── 시장 유형 카드 ───────────────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    section_title(
        f"{c_info['emoji']} {d_name} 시장 유형: {cluster_name}",
        c_info["desc"],
    )

    col_m1, col_m2 = st.columns([1, 1.4])

    with col_m1:
        st.markdown(
            f'<div style="background:{c_info["color"]}15;border:2px solid {c_info["color"]};'
            f'border-radius:12px;padding:20px;">'
            f'<div style="font-size:36px;">{c_info["emoji"]}</div>'
            f'<div style="font-weight:700;font-size:16px;color:{c_info["color"]};margin:8px 0;">{cluster_name}</div>'
            f'<div style="font-size:13px;color:#484848;">{c_info["desc"]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if len(d_row) > 0:
            row = d_row.iloc[0]
            info_row("지역 평균 하루 수익", f"₩{int(row.get('median_revpar_ao', 0)):,}")
            info_row("비활성 숙소 비율", f"{row.get('dormant_ratio', 0):.1%}")
            info_row("슈퍼호스트 비율", f"{row.get('superhost_rate', 0):.1%}")

    with col_m2:
        st.markdown("**이 지역에서 수익을 올리는 전략:**")
        for i, strat in enumerate(c_info["strategy"], 1):
            st.markdown(
                f'<div style="background:white;border:1.5px solid #EBEBEB;border-radius:8px;'
                f'padding:10px 14px;margin-bottom:6px;">'
                f'<span style="background:#FF5A5F;color:white;border-radius:50%;padding:1px 7px;'
                f'font-size:11px;font-weight:700;margin-right:8px;">{i}</span>'
                f'<span style="font-size:14px;">{strat}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── 다시 시작 버튼 ───────────────────────────────────────────────────────
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        if st.button("🔄 처음부터 다시 입력하기", key="restart", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # ── 푸터 ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:20px 0;color:#BBBBBB;font-size:12px;">
      서울 Airbnb 수익 최적화 · 데이터 기간: 2024-10 ~ 2025-09 · 32,061개 리스팅 기반
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 라우터
# ═══════════════════════════════════════════════════════════════════════════════
step = st.session_state.get("step", 1)
if step == 1:
    step1()
elif step == 2:
    step2()
elif step == 3:
    step3()
elif step == 4:
    step4()
else:
    step5()
