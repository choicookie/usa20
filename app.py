import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
from collections import Counter

# 페이지 기본 설정
st.set_page_config(page_title="미국 주간 수익률 분석기", layout="wide")

st.title("📊 미국 주간 수익률 Top 20 다빈도 종목 스크리너")
st.markdown("최근 3개월간 주간 수익률 상위 20위에 가장 많이 진입한 종목을 스크리닝하여 요약합니다.")

# 유니버스 선택
universe = st.selectbox(
    "데이터 기준 유니버스를 선택하세요:",
    ("S&P 500 (대형주 위주)", "NASDAQ 100 (기술주 위주)")
)

# 티커 목록 가져오기 함수 (데이터 소스 변경)
@st.cache_data
def get_tickers(universe_choice):
    if universe_choice == "S&P 500 (대형주 위주)":
        # S&P 500 데이터 소스를 위키피디아에서 슬릭차트로 변경 (보다 안정적)
        url = 'https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv'
        df = pd.read_csv(url)
        tickers = df['Symbol'].tolist()
    else:
         # 나스닥 100 리스트 (하드코딩으로 안정성 확보)
         tickers = [
            'AAPL', 'MSFT', 'AMZN', 'NVDA', 'META', 'TSLA', 'GOOGL', 'GOOG', 'AVGO', 'PEP',
            'COST', 'CSCO', 'TMUS', 'ADBE', 'TXN', 'CMCSA', 'AMD', 'NFLX', 'QCOM', 'INTC',
            'HON', 'INTU', 'AMGN', 'SBUX', 'AMAT', 'BKNG', 'GILD', 'MDLZ', 'ISRG', 'LRCX',
            'ADI', 'VRTX', 'REGN', 'ADP', 'PANW', 'SNPS', 'KLAC', 'CDNS', 'CSX', 'MU',
            'MELI', 'PYPL', 'MAR', 'ASML', 'CTAS', 'CRWD', 'MNST', 'ORLY', 'NXPI', 'PCAR',
            'WDAY', 'LULU', 'KDP', 'CHTR', 'MRVL', 'CPRT', 'KHC', 'DXCM', 'AEP', 'PAYX',
            'ODFL', 'CTSH', 'ROST', 'EXC', 'FAST', 'IDXX', 'BIIB', 'EA', 'VRSK', 'AZN',
            'BKR', 'CEG', 'WBD', 'GEHC', 'PDD', 'TEAM', 'DDOG', 'ZS', 'MCHP', 'ON',
            'FTNT', 'CDW', 'FANG', 'GFS', 'CSGP', 'WBA', 'SIRI', 'DLTR', 'ILMN', 'ENPH',
            'LNT', 'ZM', 'RIVN', 'LCID', 'XEL', 'EBAY', 'BMRN', 'ANSS', 'ALGN', 'WST'
         ]
    
    return [ticker.replace('.', '-') for ticker in tickers]

# 실행 버튼
if st.button("데이터 스크리닝 시작", type="primary"):
    
    # 1. 티커 가져오기
    with st.spinner(f"{universe} 종목 데이터를 준비하는 중..."):
        try:
             tickers = get_tickers(universe)
        except Exception as e:
             st.error("티커 데이터를 불러오는 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.")
             st.stop()
    
    # 2. 기간 설정 (최근 3개월)
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=90)
    
    # 3. 데이터 다운로드 및 분석
    with st.spinner(f"주가 데이터 다운로드 및 분석 중 ({start_date} ~ {end_date})... 약 1~2분 소요됩니다."):
        # yfinance 다운로드 (progress=False)
        data = yf.download(tickers, start=start_date, end=end_date, interval='1wk', progress=False)
        
        # 다운로드된 데이터 확인
        if data.empty or 'Close' not in data:
            st.error("해당 기간의 주가 데이터를 불러오지 못했습니다.")
            st.stop()
            
        # 종가 데이터 전처리 및 수익률 계산
        weekly_close = data['Close'].dropna(axis=1, thresh=len(data) // 2)
        weekly_returns = weekly_close.pct_change().dropna(how='all')
        
        top20_tickers = []
        for date, returns_series in weekly_returns.iterrows():
             # 주차별 수익률을 내림차순 정렬 후 상위 20개 추출
            top20_weekly = returns_series.sort_values(ascending=False).head(20)
            top20_tickers.extend(top20_weekly.index.tolist())
            
        ticker_counts = Counter(top20_tickers)
        
        # 결과를 데이터프레임으로 변환
        result_df = pd.DataFrame.from_dict(ticker_counts, orient='index', columns=['등장 횟수'])
        result_df = result_df.sort_values(by='등장 횟수', ascending=False)
        result_df = result_df[result_df['등장 횟수'] >= 2] # 2회 이상만 필터링
        
    st.success("스크리닝이 완료되었습니다!")
    
    # 4. 결과 화면 분할 표출
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("🏆 다빈도 종목 랭킹")
        st.dataframe(result_df, use_container_width=True)
        
    with col2:
        st.subheader("📌 인포그래픽 제작용 종목 요약")
        st.info("아래 텍스트를 복사하여 이미지 템플릿이나 보고서에 바로 활용하세요.")
        
        max_count = result_df['등장 횟수'].max() if not result_df.empty else 0
        for i in range(max_count, 1, -1):
            freq_tickers = result_df[result_df['등장 횟수'] == i].index.tolist()
            if freq_tickers:
                st.markdown(f"**■ {i}회 등장 ({len(freq_tickers)}개 종목)**")
                st.code(", ".join(freq_tickers), language="text")