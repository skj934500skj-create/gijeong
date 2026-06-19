import streamlit as st
import pandas as pd
import plotly.express as px
import os
import numpy as np

# 1. 페이지 기본 설정
st.set_page_config(
    page_title="선박 사고 데이터 분석 대시보드",
    page_icon="🚢",
    layout="wide"
)

# 2. 가상 데이터 생성 함수 (무조건 새로 생성하도록 보장)
def generate_mock_data():
    np.random.seed(42)
    rows = 200
    dates = pd.date_range(start="2024-01-01", periods=rows, freq="D")
    ship_types = ["어선", "화물선", "여객선", "유조선", "레저보트"]
    accident_types = ["충돌", "좌초", "화재/폭발", "침수", "기관고장"]
    weather_conditions = ["맑음", "흐림", "강풍", "폭우/폭설", "안개"]
    sea_states = ["잔잔함", "보통", "거침", "매우 거침"]
    regions = ["남해", "동해", "서해", "제주 인근"]
    
    data = {
        "사고일시": np.random.choice(dates, rows),
        "선박종류": np.random.choice(ship_types, rows, p=[0.4, 0.2, 0.1, 0.1, 0.2]),
        "사고유형": np.random.choice(accident_types, rows),
        "기상상태": np.random.choice(weather_conditions, rows),
        "해상상태": np.random.choice(sea_states, rows),
        "발생해역": np.random.choice(regions, rows),
        "인명피해수": np.random.randint(0, 5, rows),
        "풍속(m/s)": np.round(np.random.uniform(2, 25, rows), 1)
    }
    df = pd.DataFrame(data)
    df.to_csv("mock_data.csv", index=False, encoding="utf-8-sig")
    return df

# 무조건 깨끗한 가상 데이터 새로 로드
df = generate_mock_data()

# 날짜 데이터 변환
df["사고일시"] = pd.to_datetime(df["사고일시"])
df["월"] = df["사고일시"].dt.to_period("M").astype(str)

# 3. 사이드바 필터 UI
st.sidebar.header("⚓ 필터 설정")

# 발생해역 필터
selected_regions = st.sidebar.multiselect(
    "발생해역 선택",
    options=list(df["발생해역"].unique()),
    default=list(df["발생해역"].unique())
)

# 선박종류 필터
selected_ships = st.sidebar.multiselect(
    "선박종류 선택",
    options=list(df["선박종류"].unique()),
    default=list(df["선박종류"].unique())
)

# 필터링 적용
filtered_df = df[
    (df["발생해역"].isin(selected_regions)) & 
    (df["선박종류"].isin(selected_ships))
]

# 4. 메인 대시보드 타이틀
st.title("🚢 선박 사고 데이터 분석 및 위험 요인 대시보드")
st.markdown("전체 선박 사고 데이터를 분석하고 기상 및 선박별 위험 요인을 시각화합니다.")
st.markdown("---")

# 5. 주요 지표 (KPI Metrics)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("총 사고 건수", f"{len(filtered_df)} 건")
with col2:
    st.metric("총 인명 피해", f"{filtered_df['인명피해수'].sum()} 명")
with col3:
    st.metric("평균 풍속", f"{filtered_df['풍속(m/s)'].mean():.1f} m/s")
with col4:
    if not filtered_df.empty:
        frequent_accident = filtered_df["사고유형"].value_counts().idxmax()
        st.metric("최다 사고 유형", frequent_accident)
    else:
        st.metric("최다 사고 유형", "-")

st.markdown("---")

# 6. 시각화 섹션
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    st.subheader("📊 선박 종류별 사고 유형 현황")
    if not filtered_df.empty:
        fig1 = px.histogram(
            filtered_df, 
            x="선박종류", 
            color="사고유형", 
            barmode="group",
            labels={"count": "사고 건수"}
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.write("데이터가 없습니다.")

with row1_col2:
    st.subheader("📈 월별 사고 발생 추이")
    if not filtered_df.empty:
        trend_df = filtered_df.groupby("월").size().reset_index(name="사고건수").sort_values("월")
        fig2 = px.line(
            trend_df, 
            x="월", 
            y="사고건수", 
            markers=True,
            labels={"사고건수": "건수"}
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.write("데이터가 없습니다.")

st.markdown("---")

row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("🌪️ 위험 요인 분석: 기상 상태별 사고")
    if not filtered_df.empty:
        fig3 = px.pie(
            filtered_df, 
            names="기상상태", 
            hole=0.4
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.write("데이터가 없습니다.")

with row2_col2:
    st.subheader("🌊 해상상태 및 풍속과 인명피해 관계")
    if not filtered_df.empty:
        fig4 = px.scatter(
            filtered_df, 
            x="풍속(m/s)", 
            y="인명피해수", 
            color="해상상태",
            size="인명피해수",
            hover_data=["선박종류", "사고유형"]
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.write("데이터가 없습니다.")

# 7. 상세 데이터 표 테이블
st.markdown("---")
st.subheader("📋 필터링된 상세 사고 데이터")
st.dataframe(filtered_df.sort_values(by="사고일시", ascending=False), use_container_width=True)
