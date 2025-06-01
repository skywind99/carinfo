import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 구글시트 CSV export 주소
SHEET_URL = "https://docs.google.com/spreadsheets/d/183YjwisKFynZ0yahE9qc_E4rQZ3KY3MCsdTIjYJX0no/export?format=csv&gid=0"

# 데이터 불러오기
@st.cache_data
def load_data(url):
    df = pd.read_csv(url)
    # 첫 행에 컬럼명이 이상하게 들어있으면 자동 조정
    if df.columns[0].startswith("Unnamed"):
        df.columns = df.iloc[0]
        df = df.drop(df.index[0]).reset_index(drop=True)
    return df

df = load_data(SHEET_URL)

st.title("🚗 차량별 판매 현황 대시보드")

# 차종/모델 컬럼 자동 감지
model_col_candidates = [col for col in df.columns if any(x in str(col) for x in ["모델", "차명", "차종", "차량"])]
if not model_col_candidates:
    st.error("차량(모델) 컬럼을 찾을 수 없습니다.")
    st.stop()
model_col = model_col_candidates[0]

# 수치 컬럼 감지 (숫자형, 판매량 등)
value_col_candidates = [col for col in df.columns if any(x in str(col) for x in ["판매", "대수", "실적", "합계", "수량", "점유"])]
if not value_col_candidates:
    value_col_candidates = [col for col in df.columns if df[col].dtype in ["int64", "float64"]]
if not value_col_candidates:
    st.error("판매량(수치) 컬럼을 찾을 수 없습니다.")
    st.stop()
value_col = value_col_candidates[0]

# 모델 리스트
options = df[model_col].dropna().unique().tolist()
default_options = options[:3] if len(options) >= 3 else options

# 멀티 선택 박스
selected_models = st.multiselect(
    "차종을 선택하세요 (여러 개 가능)", options, default=default_options
)

# 선택된 모델 데이터
plot_df = df[df[model_col].isin(selected_models)]

if not plot_df.empty:
    plt.figure(figsize=(10, 6))
    plt.bar(plot_df[model_col], plot_df[value_col].astype(int))
    plt.xlabel(model_col)
    plt.ylabel(value_col)
    plt.title("차량별 판매 현황")
    st.pyplot(plt)
else:
    st.info("차량(모델)을 선택하세요!")

# 데이터 미리보기
with st.expander("원본 데이터 보기"):
    st.dataframe(df)
