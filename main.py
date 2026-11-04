import streamlit as st
import datetime
import pandas as pd
import plotly.express as px

# 페이지 기본 설정
st.set_page_config(page_title="AeroGuard - 항공 대기 계산기", layout="wide")

# 1. 핵심 계산 알고리즘 함수
def calculate_flight_metrics(flight_datetime, has_baggage, congestion_level, weather_severity):
    """
    입력된 비행 정보 및 공항 환경 수치를 바탕으로
    소요시간 및 지연 위험도를 계산하는 핵심 처리 함수
    """
    checkin_time = 40 if has_baggage else 15
    congestion_delay = congestion_level * 10
    security_time = 30
    buffer_time = 30
    
    total_minutes = checkin_time + congestion_delay + security_time + buffer_time
    recommended_arrival = flight_datetime - datetime.timedelta(minutes=total_minutes)
    
    # 위험도 점수 계산 (0 ~ 100점)
    risk_score = min(100, (weather_severity * 12) + (congestion_level * 8))
    
    return recommended_arrival, total_minutes, risk_score, checkin_time, congestion_delay, security_time

# 2. Streamlit UI 메인 화면 구성
st.title("🛫 AeroGuard: 실시간 항공편 지연 위험도 및 공항 도착 시각 계산기")
st.markdown("공항 혼잡도와 기상 상황을 종합하여 최적의 공항 출발 스케줄을 제공합니다.")

# 사이드바: 사용자 입력 Form
st.sidebar.header("📋 비행 및 공항 조건 입력")
flight_date = st.sidebar.date_input("출발 날짜", datetime.date.today())
flight_time = st.sidebar.time_input("비행기 출발 시각", datetime.time(14, 0))

has_baggage = st.sidebar.checkbox("위탁 수하물 있음", value=True)
congestion_level = st.sidebar.slider("공항 예상 혼잡도 (1:한산 ~ 5:매우혼잡)", 1, 5, 3)
weather_severity = st.sidebar.selectbox("출발지 기상 상태", [1, 2, 3, 4, 5], 
                                         format_func=lambda x: {1:"맑음/양호", 2:"구름조금", 3:"비/강풍", 4:"폭우/눈", 5:"태풍/악천후"}[x])

# 3. 데이터 처리 및 출력 실행
flight_datetime = datetime.datetime.combine(flight_date, flight_time)

if st.sidebar.button("스케줄 및 위험도 계산"):
    rec_arrival, total_min, risk, checkin, congestion, security = calculate_flight_metrics(
        flight_datetime, has_baggage, congestion_level, weather_severity
    )
    
    # 결과 요약 Metric 3열 배치
    col1, col2, col3 = st.columns(3)
    col1.metric("📌 추천 공항 도착 시각", rec_arrival.strftime("%H:%M"))
    col2.metric("⏱️ 총 예상 수속 소요 시간", f"{total_min} 분")
    col3.metric("⚠️ 항공편 지연 위험도 점수", f"{risk} 점 / 100점")
    
    # 소요 시간 파이 차트 시각화
    df_chart = pd.DataFrame({
        "수속 단계": ["체크인/수하물", "혼잡 대기", "보안검색/심사", "탑승구 여유시간"],
        "소요 시간(분)": [checkin, congestion, security, 30]
    })
    fig = px.pie(df_chart, values="소요 시간(분)", names="수속 단계", title="공항 내 단계별 예상 소요 시간 비중", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
