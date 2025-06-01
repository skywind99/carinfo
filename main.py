import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- 데이터 불러오기: CSV 파일 ---
@st.cache_data
def load_data(uploaded_file):
    df = pd.read_csv(uploaded_file)
    return df

# --- 앱 제목 ---
st.title("🚗 자동차별 판매 현황 대시보드")

# --- CSV 업로드 (또는 기본 파일 사용) ---
uploaded_file = st.file_uploader("CSV 파일 업로드", type=["csv"])
if uploaded_file is None:
    # 예시: Streamlit 환경에서는 업로드된 파일 경로를 직접 지정
    uploaded_file = "자동차차량판매정보 - 시트1 (1).csv"

try:
    df = load_data(uploaded_file)
    # 컬럼명 출력해서 유저가 확인
    st.write("데이터 미리보기", df.head())

    # 모델/차량명 컬럼 찾기(자동 감지, 예: '모델', '차종', '차량명' 등)
    col_candidates = [col for col in df.columns if "모델" in col or "차" in col]
    if not col_candidates:
        st.error("차량 모델/이름에 해당하는 컬럼을 찾을 수 없습니다.")
        st.stop()
    model_col = col_candidates[0]

    # 수량/판매대수 컬럼 자동 감지(예: '판매', '대수', '수량', '합계' 등)
    num_candidates = [col for col in df.columns if any(x in col for x in ["판매", "대수", "수량", "합계"])]
    if not num_candidates:
        st.error("판매량(수량)에 해당하는 컬럼을 찾을 수 없습니다.")
        st.stop()
    sales_col = num_candidates[0]

    # 모델(차종) 선택(다중 선택)
    models = df[model_col].dropna().unique().tolist()
    selected_models = st.multiselect(
        f"차량을 선택하세요 (여러 개 가능)", models,
        default=models[:1]
    )

    # 그래프 그리기
    if selected_models:
        plot_df = df[df[model_col].isin(selected_models)]
        plt.figure(figsize=(8, 4))
        plt.bar(plot_df[model_col], plot_df[sales_col])
        plt.xlabel("모델")
        plt.ylabel("판매대수")
        plt.title("차량별 판매 현황")
        plt.xticks(rotation=30)
        st.pyplot(plt)
    else:
        st.info("차량을 선택하면 그래프가 나타납니다.")

except Exception as e:
    st.error(f"파일을 읽거나 시각화하는 중 오류 발생: {e}")
