import streamlit as st
import pandas as pd
import re

# Google Sheets 공개 CSV 링크
SHEET_URL = "https://docs.google.com/spreadsheets/d/183YjwisKFynZ0yahE9qc_E4rQZ3KY3MCsdTIjYJX0no/export?format=csv"

@st.cache_data
def load_car_data():
    df = pd.read_csv(SHEET_URL, header=None)
    car_data = []

    for i in range(4, len(df)):
        model = str(df.iat[i, 3])
        sales = str(df.iat[i, 4])

        # 제외 조건
        if model.strip() == "총합계 :" or pd.isna(model) or "보기" not in sales:
            continue

        match = re.search(r"(\d[\d,]*)", sales)
        if match:
            sale_number = int(match.group(1).replace(",", ""))
            car_data.append({"모델": model.strip(), "판매량": sale_number})

    return pd.DataFrame(car_data)

# 데이터 로드
df = load_car_data()

# --- Streamlit UI 시작 ---
st.set_page_config(page_title="차량 판매 현황", layout="centered")
st.title("🚗 차량별 판매 현황 대시보드")

# 차량 선택 UI
car_options = df["모델"].tolist()
selected_car = st.selectbox("차량 선택", car_options)

# 세션 상태에 선택 차량 저장
if "selected_cars" not in st.session_state:
    st.session_state.selected_cars = []

if st.button("차량 추가"):
    if selected_car not in st.session_state.selected_cars:
        st.session_state.selected_cars.append(selected_car)

# 삭제 및 리스트
if st.session_state.selected_cars:
    with st.expander("✅ 선택 차량 목록"):
        for car in st.session_state.selected_cars:
            col1, col2 = st.columns([4, 1])
            col1.write(car)
            if col2.button("❌ 삭제", key=f"del_{car}"):
                st.session_state.selected_cars.remove(car)
                st.experimental_rerun()

# 그래프 및 점유율
if st.session_state.selected_cars:
    selected_df = df[df["모델"].isin(st.session_state.selected_cars)].copy()

    # 점유율 계산
    total = selected_df["판매량"].sum()
    selected_df["점유율(%)"] = (selected_df["판매량"] / total * 100).round(2)

    st.subheader("📊 판매량 그래프")
    st.bar_chart(selected_df.set_index("모델")["판매량"])

    st.subheader("📈 점유율 표")
    st.dataframe(selected_df[["모델", "판매량", "점유율(%)"]])

    # 다운로드
    csv = selected_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button("📥 CSV로 다운로드", csv, "차량_판매비교.csv", mime="text/csv")
else:
    st.info("차량을 선택하고 '차량 추가'를 눌러 그래프에 추가해보세요.")
