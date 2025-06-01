import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import altair as alt

# 구글시트 URL 및 시트 이름
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/183YjwisKFynZ0yahE9qc_E4rQZ3KY3MCsdTIjYJX0no/edit#gid=0'

# --- 구글시트 연결 (공개 문서면 CSV로 접근 가능) ---
@st.cache_data
def load_data():
    csv_url = SPREADSHEET_URL.replace('/edit#gid=', '/export?format=csv&gid=')
    df = pd.read_csv(csv_url)
    return df

df = load_data()

# --- Streamlit 앱 UI ---
st.title("🚗 차량별 판매 현황 대시보드")

# 차량 목록에서 선택 (예: '현대 쏘나타', '기아 K5' 등)
car_options = df['차종'].unique().tolist()
selected_car = st.selectbox("차량 선택", car_options)

# 세션 상태로 선택한 차량 리스트 저장
if 'selected_cars' not in st.session_state:
    st.session_state.selected_cars = []

# 버튼 클릭 시 차량 추가
if st.button("차량 추가"):
    if selected_car not in st.session_state.selected_cars:
        st.session_state.selected_cars.append(selected_car)

# 선택한 차량 목록 출력
if st.session_state.selected_cars:
    st.write("비교 차량 목록:", st.session_state.selected_cars)
    filtered_df = df[df['차종'].isin(st.session_state.selected_cars)]
    
    # 그래프 그리기 (예: 월별 판매량)
    chart = alt.Chart(filtered_df).mark_line(point=True).encode(
        x='월',
        y='판매량',
        color='차종'
    ).properties(width=700, height=400)
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.info("비교할 차량을 추가해주세요.")

