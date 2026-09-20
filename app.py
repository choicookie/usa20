import streamlit as st
import yfinance as yf
import pandas as pd
import datetime
from collections import Counter

# ---------------------------------------------------------
# 페이지 기본 설정 (맥킨지 스타일 와이드 레이아웃)
# ---------------------------------------------------------
st.set_page_config(page_title="미국 주간 수익률 분석기", layout="wide")

# CSS를 활용한 맥킨지 스타일 적용
st.markdown("""
<style>
    .stApp {
        background-color: #F8F9FA;
        color: #212529;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    h1 {
        color: #0A1C2C !important; 
        font-weight: 700 !important;
        border-bottom: 2px solid #0A1C2C;
        padding-bottom: 10px;
        margin-bottom: 30px;
    }
    h2, h3 {
        color: #1E3A5F !important;
        font-weight: 600 !important;
    }
    .dataframe {
        font-size: 14px;
    }
    div[data-testid="stAlert"] {
        background-color: #E6EEF5;
        border-left-color: #1E3A5F;
        color: #1E3A5F;
    }
    div.stButton > button:first-child {
        background-color: #0A1C2C;
        color: white;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }
    div.stButton > button:first-child:hover {
        background-color: #1E3A5F;
        color: white;
    }
    /* 마스코트 이미지 모서리를 둥글고 부드럽게 처리 */
    img {
        border-radius: 12px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 타이틀 및 마스코트 이미지 (상단 화면 분할)
# ---------------------------------------------------------
col_title, col_img = st.columns([8.5, 1.5])

with col_title:
    st.title("📊 미국 주간 모멘텀 스크리너")
    st.markdown("최근 3개월간 미국 시장(선택 유니버스) 내 **주간 수익률 상위 20위에 가장 많이 진입한 종목**과 **가장 최근 주간의 Top 20 종목**을 분석하는 대시보드입니다.")

with col_img:
    # 깃허브에 같이 업로드한 쿠키의 실제 사진 파일명을 불러옵니다.
    try:
        st.image("시바견_쿠키.png", caption="마스코트: 쿠키 🐾", use_container_width=True)
    except:
        st.info("쿠키 사진(시바견_쿠키.png)을 깃허브에 업로드해주세요!")

# ---------------------------------------------------------
# 유니버스 선택 (통합 옵션 최상단 고정)
# ---------------------------------------------------------
universe = st.selectbox(
    "데이터 기준 유니버스를 선택하세요:",
    ("S&P 500 + NASDAQ 100 (통합)", "S&P 500 (대형주 위주)", "NASDAQ 100 (기술주 위주)")
)

# 티커 목록 가져오기 함수 
@st.cache_data
def get_tickers(universe_choice):
    sp500_url = 'https://raw.githubusercontent.com/datasets/s-and-p-500-companies/master/data/constituents.csv'
    
    nasdaq100_tickers = [
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
    
    if universe_choice == "S&P 500 (대형주 위주)":
        df = pd.read_csv(sp500_url)
        tickers = df['Symbol'].tolist()
    elif universe_choice == "NASDAQ 100 (기술주 위주)":
        tickers = nasdaq100_tickers
    else:
        df = pd.read_csv(sp500_url)
        sp500_tickers = df['Symbol'].tolist()
        tickers = list(set(sp500_tickers + nasdaq100_tickers))
        
    return [ticker.replace('.', '-') for ticker in tickers]

# ---------------------------------------------------------
# 실행 메인 로직
# ---------------------------------------------------------
if st.button("데이터 스크리닝 시작", type="primary"):
    
    with st.spinner(f"{universe} 종목 데이터를 준비하는 중..."):
        try:
             tickers = get_tickers(universe)
             st.info(f"타겟 유니버스: 총 {len(tickers)}개 종목 (중복 제거 완료)")
        except Exception as e:
             st.error("티커 데이터를 불러오는 중 오류가 발생했습니다.")
             st.stop()
    
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=90)
    
    with st.spinner(f"주가 데이터 다운로드 및 분석 중 ({start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')})... 약 1~2분 소요됩니다."):
        data = yf.download(tickers, start=start_date, end=end_date, interval='1wk', progress=False)
        
        if data.empty or 'Close' not in data:
            st.error("해당 기간의 주가 데이터를 불러오지 못했습니다.")
            st.stop()
            
        weekly_close = data['Close'].dropna(axis=1, thresh=len(data) // 2)
        weekly_returns = weekly_close.pct_change().dropna(how='all')
        
        # ---------------------------------------------------------
        # [수정] 최신 주간 Top 20 추출 (기존 30 -> 20으로 변경)
        # ---------------------------------------------------------
        latest_date = weekly_returns.index[-1]
        latest_returns = weekly_returns.loc[latest_date].dropna()
        top20_latest = latest_returns.sort_values(ascending=False).head(20)
        
        top20_data = []
        rank = 1
        for ticker, ret in top20_latest.items():
            top20_data.append({
                "순위": rank,
                "티커": ticker,
                "주간 수익률(%)": round(ret * 100, 2)
            })
            rank += 1
        
        top20_df = pd.DataFrame(top20_data).set_index("순위")
        
        # [3개월 다빈도 랭킹]
        top20_tickers = []
        for date, returns_series in weekly_returns.iterrows():
            top20_weekly = returns_series.sort_values(ascending=False).head(20)
            top20_tickers.extend(top20_weekly.index.tolist())
            
        ticker_counts = Counter(top20_tickers)
        
        result_df = pd.DataFrame.from_dict(ticker_counts, orient='index', columns=['등장 횟수'])
        result_df.index.name = '티커'
        result_df = result_df.sort_values(by='등장 횟수', ascending=False)
        result_df = result_df[result_df['등장 횟수'] >= 2]
        result_df = result_df.reset_index()
        
    st.success("스크리닝이 완료되었습니다!")
    
    # ---------------------------------------------------------
    # 결과 화면 출력
    # ---------------------------------------------------------
    
    # 상단 요약 타이틀 및 데이터프레임 렌더링 변수명 변경 반영
    st.subheader(f"📌 요약: 가장 최근 주간 수익률 Top 20 (기준일: {latest_date.strftime('%Y-%m-%d')})")
    st.dataframe(top20_df.style.format({"주간 수익률(%)": "{:.2f}%"}).set_properties(**{
        'background-color': '#FFFFFF',
        'color': '#0A1C2C',
        'border-color': '#E0E0E0'
    }), use_container_width=True)
    
    st.divider() 
    
    st.subheader("🏆 모멘텀 지속성: 최근 3개월 주간 수익률 Top 20 다빈도 종목")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("**다빈도 랭킹 표**")
        st.dataframe(result_df.style.set_properties(**{
            'background-color': '#FFFFFF',
            'color': '#0A1C2C',
            'border-color': '#E0E0E0'
        }), use_container_width=True)
        
    with col2:
        st.markdown("**인포그래픽 제작용 종목 요약**")
        st.info("아래 텍스트를 복사하여 이미지 템플릿이나 브리핑 자료에 활용하세요.")
        
        max_count = result_df['등장 횟수'].max() if not result_df.empty else 0
        for i in range(max_count, 1, -1):
            freq_tickers = result_df[result_df['등장 횟수'] == i]['티커'].tolist()
            if freq_tickers:
                st.markdown(f"**■ {i}회 등장 ({len(freq_tickers)}개 종목)**")
                st.code(", ".join(freq_tickers), language="text")