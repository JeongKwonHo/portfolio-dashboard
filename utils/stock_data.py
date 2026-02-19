import yfinance as yf
from pykrx import stock as krx_stock
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional


def get_kr_price(ticker: str) -> Optional[float]:
    """한국 주식 현재가 조회 (pykrx)"""
    try:
        today = datetime.now()
        end = today.strftime('%Y%m%d')
        start = (today - timedelta(days=7)).strftime('%Y%m%d')

        df = krx_stock.get_market_ohlcv_by_date(start, end, ticker)
        if df is not None and not df.empty:
            return float(df['종가'].iloc[-1])
        return None
    except Exception as e:
        print(f"한국 주식 시세 조회 실패 ({ticker}): {e}")
        return None


def get_us_price(ticker: str) -> Optional[float]:
    """미국 주식 현재가 조회 (yfinance)"""
    try:
        ticker_obj = yf.Ticker(ticker)
        hist = ticker_obj.history(period='5d')
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
        return None
    except Exception as e:
        print(f"미국 주식 시세 조회 실패 ({ticker}): {e}")
        return None


def get_current_price(ticker: str, market: str) -> Optional[float]:
    if market == 'KR':
        return get_kr_price(ticker)
    else:
        return get_us_price(ticker)


def get_current_prices(portfolio_df: pd.DataFrame) -> pd.DataFrame:
    df = portfolio_df.copy()
    prices = []

    for _, row in df.iterrows():
        price = get_current_price(row['ticker'], row['market'])
        prices.append(price)

    df['current_price'] = prices
    return df
