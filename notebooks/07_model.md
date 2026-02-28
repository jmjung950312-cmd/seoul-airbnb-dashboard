**1. 개요 (Objective)**
기존의 단일 RevPAR 예측 모델을 **ADR(가격 가치) 모델**과 **Occupancy(수요 반응) 모델**로 이원화하여, 호스트에게 "왜 내 수익이 이 모양인가?"에 대한 구조적 진단과 "가격을 바꾸면 어떻게 되는가?"에 대한 정교한 시뮬레이션을 제공함.

**2. 모델 아키텍처 (Dual-Model Structure)
2.1. Model A: ADR 가치 모델 (Market Pricing)**
• **목적**: 숙소의 하드웨어적 스펙이 시장에서 인정받는 '적정 가격'을 산출.
• **타겟 변수**: `log1p(adr)` (또는 높은 RevPAR를 유지하는 상위 그룹의 ADR)
• **핵심 피처 (Fixed Specs)**: 자치구 클러스터, 위경도 기반 POI 밀도, 숙소 유형, 수용 인원, 침실/욕실 수, 편의시설(Wifi, 주차 등).
• **제약 조건**: `bedrooms`, `capacity` 등 물리적 크기 관련 변수는 ADR에 양(+)의 영향을 주도록 **Monotonic Constraint** 적용.

**2.2. Model B: Occupancy 예측 모델 (Demand Sensitivity)**
• **목적**: 설정된 가격 및 운영 정책에 따른 예약 확률 예측.
• **타겟 변수**: `ttm_occupancy` (0~1 사이 값)
• **핵심 피처 (Actionable Levers)**: **Model A에서 예측된 ADR 대비 실제 가격 격차(Price Gap)**, 최소 숙박일, 즉시 예약 여부, 리뷰 수, 평점, 사진 수.
• **핵심 논리**: 가격이 오를수록 수요가 떨어지는 **가격 탄력성(Price Elasticity)** 학습.

**2.3. Derived Metric: 통합 RevPAR & Calibration**
• **공식**: $RevPAR_{pred} = ADR_{pred} \times Occ_{pred}$
• **보정**: 오차 증폭 방지를 위해 실제 RevPAR 직접 예측 모델과 앙상블하거나, 클러스터별 평균 수익으로 Calibration 진행.

**3. 전략적 진단 엔진 (2D Positioning & SHAP)
3.1. 2D 전략 맵 (Positioning Matrix)**
자치구/클러스터 내 상대적 위치를 기반으로 4분면 정의:
1. **Premium Winner (고가·고점유)**: 시장 지배적 숙소.
2. **Overpriced Risk (고가·저점유)**: 가격 인하 또는 가치 개선 필요.
3. **Volume King (저가·고점유)**: 박리다매형. 가격 인상 테스트 권장.
4. **Stagnant (저가·저점유)**: 전면적 리뉴얼 필요.

**3.2. 분리형 SHAP 분석 (Dual-Driver Insight)**
• **Price SHAP**: "위치 프리미엄이 ₩15,000 상승을 견인 중" (하드웨어 가치 측정)
• **Demand SHAP**: "높은 가격 설정이 예약률을 12% 깎아먹는 중" (운영 정책 진단)

**4. 수익 시뮬레이션 엔진 (What-If Analysis)
4.1. 가격 탄력성 시나리오**
• 현재 가격 기준 $\pm 5\%, 10\%, 20\%$ 구간에서 Model B를 재실행.
• $RevPAR$가 최대화되는 **Optimal Price Point** 도출.
• **Guardrail**: 시뮬레이션 범위는 해당 클러스터의 $Q1~Q3$ 가격 분포 내로 제한하여 모델의 외삽(Extrapolation) 오류 방지.

**4.2. 순이익(Net Profit) 최적화**
• $Profit = (RevPAR_{pred} \times 30) - OPEX(사용자 입력)$
• 매출 극대화가 아닌 **호스트의 실제 순이익이 가장 높은 지점**을 권장가로 제시.

**5. 구현 체크리스트 (For Claude)**
1. **데이터 분할**: 클러스터별 특성이 강하므로 `Cluster_Rank`를 Stratify 레이블로 활용하여 Train/Test 분리.
2. **구간 예측 적용**: 점 예측뿐만 아니라 **CQR(Conformal Quantile Regression)**을 적용하여 80% 신뢰 구간(PI) 산출.
3. **오차 보정**: ADR 모델과 Occupancy 모델의 결과값이 실제 RevPAR 분포와 일치하는지 확인하기 위해 **Mean Absolute Error(MAE)** 외에 **Residual Analysis** 수행.
4. **사용자 입력 인터페이스**: OPEX(운영비) 변수를 수용할 수 있는 `predict_with_profit` 함수 구현.