import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 구글시트 또는 CSV 파일 불러오기(사용자 업로드 가능)
uploaded_file = st.file_uploader("CSV 파일을 업로드 하세요", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    SHEET_URL = "https://docs.google.com/spreadsheets/d/183YjwisKFynZ0yahE9qc_E4rQZ3KY3MCsdTIjYJX0no/export?format=csv&gid=0"
    df = pd.read_csv(SHEET_URL)

# 컬럼명 확인(첫 행에 이상한 값이 있으면 헤더 자동조정)
if df.columns[0].startswith("Unnamed"):
    df.columns = df.iloc[0]
    df = df.drop(df.index[0]).reset_index(drop=True)

# 차량 모델(차종, 차명 등) 컬럼 자동 감지
model_col_candidates = [col for col in df.columns if any(x in str(col) for x in ["모델", "차명", "차종", "차량"])]
if not model_col_candidates:
    st.error(f"차량 모델/이름에 해당하는 컬럼을 찾을 수 없습니다.\n컬럼 목록: {list(df.columns)}")
    st.stop()
model_col = model_col_candidates[0]

# 판매량/수량 컬럼 자동 감지
sales_col_candidates = [col for col in df.columns if any(x in str(col) for x in ["판매", "대수", "수량", "합계"])]
if not sales_col_candidates:
    st.error(f"판매량(수량)에 해당하는 컬럼을 찾을 수 없습니다.\n컬럼 목록: {list(df.columns)}")
    st.stop()
sales_col = sales_col_candidates[0]

# 선택 UI
models = df[model_col].dropna().unique().tolist()
selected_models = st.multiselect("차량을 선택하세요 (복수 선택 가능)", models, default=models[:1])

# 그래프 그리기
if selected_models:
    plot_df = df[df[model_col].isin(selected_models)]
    try:
        plot_df[sales_col] = plot_df[sales_col].astype(int)
    except:
        plot_df[sales_col] = pd.to_numeric(plot_df[sales_col].str.replace(",", ""), errors="coerce").fillna(0).astype(int)
    plt.figure(figsize=(8, 4))
    plt.bar(plot_df[model_col], plot_df[sales_col])
    plt.xlabel("모델")
    plt.ylabel("판매대수")
    plt.title("차량별 판매 현황")
    plt.xticks(rotation=30)
    st.pyplot(plt)
else:
    st.info("차량을 선택하면 그래프가 나타납니다.")
