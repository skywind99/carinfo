import streamlit as st
import pandas as pd
import re

# Google Sheets에서 CSV 형식으로 가져올 수 있도록 링크 수정
SPREADSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/183YjwisKFynZ0yahE9qc_E4rQZ3KY3MCsdTIjYJX0no/export?format=csv"

# 캐시로 불러오기
@st.cache_data
def load_and_clean_data():
    df_raw = pd.read_csv(SPREADSHEET_CSV_URL, header=None)

    car_data = []

    for row in df_raw.itertuples():
        # 좌측 열: 국산차 모델
        left_model = str(row[2]).strip() if len(row) > 2 else None
        left_sales = str(row[3]).strip() if len(row) > 3 else None

        if left_model and "그래프로" in left_sales:
            match = re.search(r"(\d[\d,]*)", left_sales)
            if match:
                sales = int(match.group(1).replace(",", ""))
                car_data.append({"모델": left_model, "판매량": sales, "구분": "국산차"})

        # 우측 열: 수입차 모델
        right_model = str(row[8]).strip() if len(row) > 8 else None
        right_sales = str(row[9]).strip() if len(row) > 9 else None

        if right_model and "그래프로" in right_sales:
            match = re.search(r"(\d[\d,]*)", right_sales)
            if match:
                sales = int(match.group(1).replace(",", ""))
                car_data.append({"모델": right_model, "판매량": sales, "구분": "수입차"})

    return pd.DataFrame(car_data)

# 데이터 불러오기
df = load_and_clean_data()

# Streamlit 앱
st.title("🚗 차량별 판매 현황 대시보드")

car_options = df["모델"].tolist()
selected_car = st.selectbox("차량 선택", car_options)

# 차량 비교 목록 유지
if "selected_cars" not in st.session_state:
    st.session_state.selected_cars = []

if st.button("차량 추가"):
    if selected_car not in st.session_state.selected_cars:
        st.session_state.selected_cars.append(selected_car)

if st.session_state.selected_cars:
    st.subheader("✅ 선택한 차량 판매량 비교")
    selected_df = df[df["모델"].isin(st.session_state.selected_cars)]
    st.bar_chart(selected_df.set_index("모델")["판매량"])
else:
    st.info("비교할 차량을 선택하고 추가해주세요.")
