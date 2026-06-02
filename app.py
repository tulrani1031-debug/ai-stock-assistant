import yfinance as yf
import pandas as pd
# 뉴스 감성 분석 및 AI 추론은 LangChain 등을 통해 연결
# from langchain import OpenAI 

def analyze_stock(ticker_symbol):
    # 1. 데이터 로드
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="3mo")
    
    # 2. 기술적 지표 계산 (SMA 20, RSI)
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    df['RSI'] = 100 - (100 / (1 + (gain / loss)))
    
    # 3. 뉴스 데이터 수집 및 분석 (예시)
    # news = fetch_news(ticker_symbol) 
    # sentiment = analyze_sentiment(news)
    
    # 4. 결론 도출 (AI Agent가 판단)
    current_price = df['Close'].iloc[-1]
    last_rsi = df['RSI'].iloc[-1]
    
    return f"{ticker_symbol} 분석 완료: 현재가 {current_price:.2f}, RSI {last_rsi:.2f}."