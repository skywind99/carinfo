import streamlit as st
import pandas as pd
import re

# Google Sheets CSV 주소
SPREADSHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/183YjwisKFynZ0yahE9qc_E4rQZ3KY3MCsdTIjYJX0no/export?format=csv"

@st.cache_data
def load_data():
    df_raw = pd.read_csv(SPREADSHEET_CSV_URL, header=None)
    car_data = []

    for row in df_raw.itertuples():
        # 국산차
        left_model = str(row[2]).strip() if len(row) > 2 else None
        left_sales = str(row[3]).strip() if len(row) > 3 else None
        if left_model and left_sales:
            match = re.search(r"(\d[\d,]*)", left_sales)
            if match:
                sales = int(match.group(1).replace(",", ""))
                car_data.append({"모델": left_model, "판매량": sales, "구분": "국산차"})

                

        # 수입차
        right_model = str(row[8]).strip() if len(row) > 8 else None
        right_sales = str(row[9]).strip() if len(row) > 9 else None
        if left_model and left_sales:
            match = re.search(r"(\d[\d,]*)", left_sales)
            if match:
                sales = int(match.group(1).replace(",", ""))
                car_data.append({"모델": left_model, "판매량": sales, "구분": "수입차"})

    return pd.DataFrame(car_data)

df = load_data()

# Streamlit 앱 시작
st.title("🚗 차량별 판매 현황 대시보드")

car_options = df["모델"].tolist()
selected_car = st.selectbox("차량 선택", car_options)

# 세션 상태
if "selected_cars" not in st.session_state:
    st.session_state.selected_cars = []

# 차량 추가
if st.button("차량 추가"):
    if selected_car not in st.session_state.selected_cars:
        st.session_state.selected_cars.append(selected_car)

# 선택한 차량 삭제 기능
if st.session_state.selected_cars:
    with st.expander("선택한 차량 목록 및 삭제"):
        for car in st.session_state.selected_cars:
            col1, col2 = st.columns([4, 1])
            col1.write(f"✅ {car}")
            if col2.button("❌ 삭제", key=f"del_{car}"):
                st.session_state.selected_cars.remove(car)
                st.experimental_rerun()

# 비교 그래프
if st.session_state.selected_cars:
    selected_df = df[df["모델"].isin(st.session_state.selected_cars)].copy()

    st.subheader("📊 판매량 비교")
    st.bar_chart(selected_df.set_index("모델")["판매량"])

    # 점유율 계산
    total = selected_df["판매량"].sum()
    selected_df["점유율(%)"] = (selected_df["판매량"] / total * 100).round(2)

    st.subheader("📈 점유율 (%) 비교")
    st.dataframe(selected_df[["모델", "판매량", "점유율(%)", "구분"]])

    # 다운로드 버튼
    csv = selected_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 CSV로 다운로드",
        data=csv,
        file_name="차량_판매_비교.csv",
        mime='text/csv'
    )
else:
    st.info("비교할 차량을 선택해주세요.")
