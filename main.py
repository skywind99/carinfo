import streamlit as st
import pandas as pd
import re

# ✅ Google Sheets에서 CSV로 직접 가져오기
SHEET_URL = "https://docs.google.com/spreadsheets/d/183YjwisKFynZ0yahE9qc_E4rQZ3KY3MCsdTIjYJX0no/export?format=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(SHEET_URL, header=None)

    def extract_car_data(start_row, model_col, sales_col, label):
        car_data = []
        for i in range(start_row, len(df)):
            model = str(df.iat[i, model_col])
            sales = str(df.iat[i, sales_col])

            if model.strip() == "총합계 :" or pd.isna(model) or "보기" in model:
                continue

            if "그래프로" in sales:
                match = re.search(r"(\d[\d,]*)", sales)
                if match:
                    sale_number = int(match.group(1).replace(",", ""))
                    car_data.append({"모델": model.strip(), "판매량": sale_number, "구분": label})
        return car_data

    # 국산차: 열 3~4 / 수입차: 열 12~13
    domestic = extract_car_data(start_row=4, model_col=3, sales_col=4, label="국산차")
    imported = extract_car_data(start_row=4, model_col=12, sales_col=13, label="수입차")

    return pd.DataFrame(domestic + imported)

df = load_data()

# --- Streamlit 앱 UI ---
st.title("🚘 차량별 판매량 비교 대시보드")

car_options = df["모델"].tolist()
selected_car = st.selectbox("차량 선택", car_options)

# 선택한 차량 리스트 세션에 저장
if "selected_cars" not in st.session_state:
    st.session_state.selected_cars = []

# 차량 추가
if st.button("차량 추가"):
    if selected_car not in st.session_state.selected_cars:
        st.session_state.selected_cars.append(selected_car)

# 삭제 기능
if st.session_state.selected_cars:
    with st.expander("🚗 선택한 차량 목록 및 삭제"):
        for car in st.session_state.selected_cars:
            col1, col2 = st.columns([5, 1])
            col1.write(f"✅ {car}")
            if col2.button("삭제", key=f"del_{car}"):
                st.session_state.selected_cars.remove(car)
                st.experimental_rerun()

# 비교 그래프
if st.session_state.selected_cars:
    selected_df = df[df["모델"].isin(st.session_state.selected_cars)].copy()

    st.subheader("📊 판매량 비교")
    st.bar_chart(selected_df.set_index("모델")["판매량"])

    # 점유율 계산
    total_sales = selected_df["판매량"].sum()
    selected_df["점유율(%)"] = (selected_df["판매량"] / total_sales * 100).round(2)

    st.subheader("📈 점유율 테이블")
    st.dataframe(selected_df[["모델", "판매량", "점유율(%)", "구분"]])

    # 다운로드 버튼
    csv = selected_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 CSV로 다운로드",
        data=csv,
        file_name="차량_판매_비교.csv",
        mime="text/csv",
    )
else:
    st.info("차량을 선택하고 '차량 추가' 버튼을 눌러 비교하세요.")
