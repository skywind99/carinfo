import streamlit as st
import pandas as pd
import re

# Google Sheets 공개 CSV 링크
SHEET_URL = "https://docs.google.com/spreadsheets/d/183YjwisKFynZ0yahE9qc_E4rQZ3KY3MCsdTIjYJX0no/export?format=csv"

@st.cache_data
def load_car_data():
    try:
        df = pd.read_csv(SHEET_URL, header=None)
        car_data = []
        
        for i in range(4, len(df)):
            model = str(df.iat[i, 3])
            sales = str(df.iat[i, 4])
            
            # 제외 조건 개선
            if (model.strip() == "총합계 :" or 
                pd.isna(model) or 
                model.strip() == "" or 
                model.strip() == "nan" or
                "보기" not in sales):
                continue
            
            # 판매량 추출 정규식 개선
            match = re.search(r"(\d[\d,]*)", sales)
            if match:
                sale_number = int(match.group(1).replace(",", ""))
                car_data.append({"모델": model.strip(), "판매량": sale_number})
        
        return pd.DataFrame(car_data)
    
    except Exception as e:
        st.error(f"데이터 로드 중 오류가 발생했습니다: {e}")
        return pd.DataFrame(columns=["모델", "판매량"])

# 데이터 로드
df = load_car_data()

# --- Streamlit UI 시작 ---
st.set_page_config(page_title="차량 판매 현황", layout="wide")
st.title("🚗 차량별 판매 현황 대시보드")

# 데이터가 로드되었는지 확인
if df.empty:
    st.warning("데이터를 불러올 수 없습니다. 시트 URL을 확인해주세요.")
    st.stop()

# 전체 통계 표시
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 차종 수", len(df))
with col2:
    st.metric("총 판매량", f"{df['판매량'].sum():,}대")
with col3:
    st.metric("평균 판매량", f"{df['판매량'].mean():.0f}대")

st.divider()

# 차량 선택 UI
col1, col2 = st.columns([3, 1])
with col1:
    car_options = df["모델"].tolist()
    selected_car = st.selectbox("차량 선택", car_options)
with col2:
    st.write("")  # 여백
    add_button = st.button("🚗 차량 추가", use_container_width=True)

# 세션 상태에 선택 차량 저장
if "selected_cars" not in st.session_state:
    st.session_state.selected_cars = []

if add_button:
    if selected_car not in st.session_state.selected_cars:
        st.session_state.selected_cars.append(selected_car)
        st.success(f"{selected_car}가 추가되었습니다!")
    else:
        st.warning(f"{selected_car}는 이미 선택되어 있습니다.")

# 선택된 차량 목록 표시
if st.session_state.selected_cars:
    st.subheader("✅ 선택된 차량 목록")
    
    # 차량 목록을 테이블 형태로 표시
    for i, car in enumerate(st.session_state.selected_cars):
        col1, col2, col3 = st.columns([0.5, 3, 1])
        col1.write(f"{i+1}.")
        col2.write(car)
        if col3.button("❌", key=f"del_{car}", help="삭제"):
            st.session_state.selected_cars.remove(car)
            st.rerun()  # st.experimental_rerun() 대신 st.rerun() 사용
    
    st.divider()
    
    # 선택된 차량들의 데이터 필터링
    selected_df = df[df["모델"].isin(st.session_state.selected_cars)].copy()
    
    # 점유율 계산 (선택된 차량들 중에서)
    total_selected = selected_df["판매량"].sum()
    selected_df["점유율(%)"] = (selected_df["판매량"] / total_selected * 100).round(2)
    
    # 판매량 기준으로 정렬
    selected_df = selected_df.sort_values("판매량", ascending=False)
    
    # 그래프와 표를 나란히 배치
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 판매량 비교 그래프")
        st.bar_chart(selected_df.set_index("모델")["판매량"])
    
    with col2:
        st.subheader("📈 상세 데이터")
        st.dataframe(
            selected_df[["모델", "판매량", "점유율(%)"]],
            use_container_width=True,
            hide_index=True
        )
    
    # 추가 분석 정보
    st.subheader("📋 분석 요약")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("선택 차량 총 판매량", f"{total_selected:,}대")
    with col2:
        best_seller = selected_df.iloc[0]
        st.metric("최고 판매 차량", best_seller["모델"], f"{best_seller['판매량']:,}대")
    with col3:
        market_share = (total_selected / df["판매량"].sum() * 100)
        st.metric("전체 시장 점유율", f"{market_share:.1f}%")
    
    # 다운로드 기능
    st.divider()
    csv = selected_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        "📥 CSV로 다운로드",
        csv,
        f"차량_판매비교_{len(st.session_state.selected_cars)}개차종.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    # 전체 초기화 버튼
    if st.button("🗑️ 전체 초기화", type="secondary"):
        st.session_state.selected_cars = []
        st.rerun()

else:
    st.info("👆 위에서 차량을 선택하고 '차량 추가' 버튼을 눌러 비교 분석을 시작해보세요!")
    
    # 전체 데이터 미리보기
    with st.expander("📋 전체 차량 데이터 미리보기"):
        preview_df = df.sort_values("판매량", ascending=False).head(10)
        st.dataframe(preview_df, use_container_width=True, hide_index=True)
