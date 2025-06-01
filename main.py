import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --- 구글시트 연동을 위한 서비스 계정 키(JSON) 준비 안내 ---
st.info("처음 1회만 구글 클라우드에서 서비스 계정 발급 후 JSON 파일을 업로드해야 합니다.")
st.markdown("""
**발급 방법:**
1. https://console.developers.google.com/ 에서 프로젝트 생성
2. Google Drive API & Sheets API 활성화
3. 서비스 계정 생성 > 키 발급(json)
4. 해당 서비스 계정 이메일을 구글시트 '공유'로 등록(편집자)
""")

uploaded_json = st.file_uploader("구글 서비스계정 JSON 파일 업로드", type=["json"])
if not uploaded_json:
    st.stop()

# --- 구글 시트 데이터 불러오기 ---
@st.cache_data
def load_sheet(sheet_key, worksheet_name, json_file):
    # 인증 및 시트 접근
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        pd.read_json(json_file).to_dict(orient="records")[0], scope
    )
    client = gspread.authorize(creds)
    worksheet = client.open_by_key(sheet_key).worksheet(worksheet_name)
    # 데이터프레임 변환
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
    return df

SHEET_KEY = "183YjwisKFynZ0yahE9qc_E4rQZ3KY3MCsdTIjYJX0no"
SHEET_NAME = "시트1"

try:
    df = load_sheet(SHEET_KEY, SHEET_NAME, uploaded_json)
    st.write("데이터 미리보기", df.head())

    # 모델/차량명 컬럼 자동 감지
    col_candidates = [col for col in df.columns if "모델" in col or "차" in col]
    if not col_candidates:
        st.error("차량 모델/이름에 해당하는 컬럼을 찾을 수 없습니다.")
        st.stop()
    model_col = col_candidates[0]

    # 수량/판매대수 컬럼 자동 감지
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
        plot_df = df_
