# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

서울 에어비앤비 RevPAR 최적화 분석 프로젝트. 32,061개 리스팅, 42개 컬럼, 데이터 기간 2024-10-01 ~ 2025-09-30 (TTM 12개월).

**분석 목적**: 두 관점에서 RevPAR 최적화 포인트 탐색
- **호스트 관점**: 물건 단위에서 호스트가 통제 가능한 변수 → RevPAR 영향 분석
- **플랫폼 관점**: 자치구 단위 RevPAR 패턴, 군집 분류 기반 시장 포지셔닝

## Quick Start

```bash
jupyter lab          # 분석 노트북 실행
streamlit run app.py # RevPAR 대시보드 실행
```

## Data Files

```
data/raw/
  seoul_airbnb_cleaned.csv       # 원본 전처리 완료 데이터 (32,061행 × 42열)
  seoul_airbnb_geo_masked.csv    # 좌표 마스킹 버전

data/processed/
  seoul_airbnb_features.csv      # 피처 엔지니어링 완료본
  X_train_host.csv / X_test_host.csv
  y_train_host_log.csv / y_train_host_orig.csv
  y_test_host_log.csv / y_test_host_orig.csv
  district_aggregated.csv        # 자치구 집계 통계
  district_clustered.csv         # K-Means 군집 결과
```

## Notebook Execution Order

| 번호 | 파일 | 내용 |
|------|------|------|
| 00 | `notebooks/00_quick_eda.ipynb` | 전체 데이터 개요 |
| 01 | `notebooks/01_host_eda.ipynb` | 호스트 관점 EDA — H1~H5 가설 검증 |
| 02 | `notebooks/02_host_preprocessing.ipynb` | Active+Operating 서브셋 전처리 및 train/test 분할 |
| 03 | `notebooks/03_host_modeling.ipynb` | LightGBM + RF + Ridge 5-Fold CV, SHAP 분석 *(스킵)* |
| 04 | `notebooks/04_platform_eda.ipynb` | 플랫폼 관점 EDA |
| 05 | `notebooks/05_platform_clustering.ipynb` | 자치구 K-Means(k=4) 군집 분류 |
| 06 | `notebooks/06_platform_insights.ipynb` | 플랫폼 인사이트 도출 |

`pre_notebook/` 폴더의 `_final.ipynb`에서 전처리가 이미 완료되었음 — 재실행 불필요.

## Analysis Rules

### Analysis SOP

전체 분석 표준은 `SOP_ANALYSIS.json`과 `SOP_ANALYSIS.md`를 참조. 핵심 내용:

**데이터 전처리 (완료)** — `_final.ipynb`에서 처리됨, 추가 전처리 불필요:
- district 결측치: Spatial Join으로 채움
- 이상치 제거: `min_nights > 730`, `ttm_avg_rate > 2,000,000`
- 외부 데이터 병합: POI, 환율, 인구

**분석 필터**:
- 전체 32,061개 분석 + Active+Operating(`refined_status=='Active'` & `operation_status=='Operating'`) 14,399개 서브셋 별도 분석

**제외 컬럼**: `exng`, `ttm_exng` (상수), `nearest_poi_image` (23.9% 결측)

### KPI Definitions

```python
# RevPAR = ADR × Occupancy Rate
revpar       = ttm_revpar          # 12개월 TTM
recent_revpar = l90d_revpar        # 최근 90일

# 필수 파생 변수
revpar_trend = (l90d_revpar - ttm_revpar/4) / (ttm_revpar/4 + 1e-6)
log_ttm_revpar = np.log1p(ttm_revpar)
is_active_operating = (refined_status=='Active') & (operation_status=='Operating')

# 모델 타겟 (log1p 변환 사용 — skewness=3.76)
target = np.log1p(ttm_revpar)
# 역변환
y_pred_original = np.expm1(y_pred_log)
```

## Modeling

### Data Leakage — 모델링 시 반드시 제외할 특성

| 특성 | 누수 등급 | 사유 |
|------|----------|------|
| `revpar_vs_district_median` | CRITICAL | ttm_revpar 직접 파생 |
| `revpar_trend` | HIGH | ttm_revpar 구성요소 포함 |
| `price_efficiency` | MEDIUM | ttm_avg_rate / ttm_occupancy |
| `ttm_occupancy`, `ttm_avg_rate`, `ttm_revenue` | 제외 | RevPAR 직접 구성요소 |
| `l90d_revpar`, `l90d_occupancy`, `l90d_avg_rate`, `l90d_revenue` | 제외 | 타겟 관련 기간별 파생 |
| `revpar_percentile`, `log_ttm_revpar` | 제외 | 타겟 직접 변환 |

**모델 입력 피처 (호스트 관점)**:
`room_type`, `superhost`, `instant_book`, `bedrooms_group`, `baths_group`, `guests_group`, `min_nights`, `extra_guest_fee_policy`, `rating_overall`, `photos_count`, `num_reviews`, `nearest_poi_dist_km`, `nearest_poi_type_name`, `photos_tier`, `review_rate`, `poi_dist_category`

### Modeling Standards

```python
# 재현성 — 항상 동일한 seed 사용
RANDOM_SEED = 42
train_test_split(..., test_size=0.2, random_state=42)
KFold(n_splits=5, shuffle=True, random_state=42)

# 모델 구성 (호스트 관점)
models = [LightGBM, RandomForest, Ridge, DummyRegressor(strategy='median')]

# 평가 지표
primary   = R²
secondary = [MAE, RMSE, MAPE]

# 예측값 범위 검증
assert (y_pred >= 0).all() and (y_pred <= 2_000_000).all()

# 플랫폼 관점 (자치구 단위, n=25 소표본)
Ridge + LeaveOneOut CV
```

## Visualization Standards

```python
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'AppleGothic'
plt.rcParams['axes.unicode_minus'] = False  # 모든 노트북에 필수

# 기준
figsize_max = (14, 8)
subplot_max = '2×2'
color_palette = 'Set2'
dpi = 100
```

시각화 결과는 `reports/` 폴더에 `fig_XX_*.png` 형식으로 저장.

## Naming Conventions

```python
# 파생 피처 접두사
feat_*      # 일반 피처
kpi_*       # KPI 관련
dist_*      # 자치구(district) 집계 통계
```

## Key Domain Insights

- **슈퍼호스트 프리미엄**: Active+Operating 기준 +83.1% RevPAR (₩61,205 vs ₩31,825)
- **전체 Dormant 비율**: 54.3% — 시장 건전성 핵심 리스크
- **사진 최적 구간**: 21~35장 (그 이상은 한계효용 체감)
- **최소숙박일 최적점**: 2~3박
- **공급 최대 자치구**: 마포구 (~21%), RevPAR 압박 구조
- **TTM RevPAR 중위값**: ₩8,868 (전체) / ₩47,850 (Active+Operating)

## Agent Outputs

`agents/` 폴더에 분석 파이프라인 각 단계의 JSON 결과가 저장되어 있음:

| 파일 | 내용 |
|------|------|
| `domain_research.json` | 도메인 특성, KPI 정의, 경고사항 |
| `hypotheses.json` | H1~H9 가설 정의 |
| `kpi_calculation.json` | KPI 계산 결과 |
| `statistical_analysis.json` | 통계 검증 결과 |
| `eda_*.json` | EDA 세 에이전트(벤치마크, 세그먼트, 시각화) 결과 |
| `feature_engineering.json` | 피처 엔지니어링 명세 |
| `synthesis_and_modeling.json` | 종합 모델링 계획 |
| `model_review.json` | 모델 리뷰 결과 (CONDITIONAL APPROVED) |
