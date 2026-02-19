import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
import os
from datetime import datetime

from utils.stock_data import get_current_prices
from utils.calculations import calculate_portfolio

st.set_page_config(
    page_title="포트폴리오 수익률 추적기",
    page_icon="📈",
    layout="wide"
)

DATA_FILE = "data/portfolio.csv"


def load_portfolio() -> pd.DataFrame:
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE, dtype={"ticker": str})
    return pd.DataFrame(columns=["ticker", "name", "market", "shares", "avg_price", "currency"])


def save_portfolio(df: pd.DataFrame):
    Path("data").mkdir(exist_ok=True)
    df.to_csv(DATA_FILE, index=False)


# ---- 헤더 ----
st.title("📈 포트폴리오 수익률 추적기")
st.caption(f"마지막 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

portfolio = load_portfolio()

# ---- 사이드바 ----
with st.sidebar:
    st.header("➕ 종목 추가")

    market = st.selectbox("시장", ["KR (한국)", "US (미국)"])
    market_code = "KR" if market.startswith("KR") else "US"

    ticker = st.text_input("종목코드", placeholder="KR: 005930  |  US: AAPL")
    name = st.text_input("종목명", placeholder="삼성전자  |  Apple")
    shares = st.number_input("보유 수량", min_value=0.0, step=1.0, format="%.2f")
    avg_price = st.number_input(
        "평균 매수가",
        min_value=0.0,
        step=100.0 if market_code == "KR" else 1.0,
        format="%.2f"
    )

    if st.button("추가하기", type="primary", use_container_width=True):
        if ticker and name and shares > 0 and avg_price > 0:
            ticker_clean = ticker.strip().upper() if market_code == "US" else ticker.strip()
            if not portfolio.empty and ticker_clean in portfolio["ticker"].values:
                st.error("이미 추가된 종목입니다.")
            else:
                currency = "KRW" if market_code == "KR" else "USD"
                new_row = pd.DataFrame([{
                    "ticker": ticker_clean,
                    "name": name.strip(),
                    "market": market_code,
                    "shares": shares,
                    "avg_price": avg_price,
                    "currency": currency
                }])
                portfolio = pd.concat([portfolio, new_row], ignore_index=True)
                save_portfolio(portfolio)
                st.success(f"✅ {name} 추가 완료!")
                st.rerun()
        else:
            st.error("모든 항목을 입력해주세요.")

    if not portfolio.empty:
        st.divider()
        st.header("🗑️ 종목 삭제")
        options = ["선택하세요"] + portfolio["name"].tolist()
        stock_to_delete = st.selectbox("삭제할 종목", options, label_visibility="collapsed")
        if st.button("삭제하기", type="secondary", use_container_width=True):
            if stock_to_delete != "선택하세요":
                portfolio = portfolio[portfolio["name"] != stock_to_delete]
                save_portfolio(portfolio)
                st.success(f"🗑️ {stock_to_delete} 삭제됨")
                st.rerun()

# ---- 메인 콘텐츠 ----
if portfolio.empty:
    st.info("👈 왼쪽 사이드바에서 종목을 추가해주세요.")
    st.subheader("입력 예시")
    st.dataframe(pd.DataFrame([
        {"종목코드": "005930", "종목명": "삼성전자", "시장": "KR", "수량": 10, "평균매수가": "70,000 KRW"},
        {"종목코드": "AAPL", "종목명": "Apple", "시장": "US", "수량": 5, "평균매수가": "150.00 USD"},
    ]), hide_index=True, use_container_width=True)
else:
    with st.spinner("📡 시세 조회 중..."):
        portfolio_with_prices = get_current_prices(portfolio)

    result = calculate_portfolio(portfolio_with_prices)

    if result.empty:
        st.error("시세를 가져오지 못했습니다. 종목코드를 확인해주세요.")
        st.stop()

    # ---- 요약 지표 ----
    kr_stocks = result[result["market"] == "KR"]
    us_stocks = result[result["market"] == "US"]

    num_cols = 1 + (1 if not kr_stocks.empty else 0) + (1 if not us_stocks.empty else 0) + 1
    cols = st.columns(num_cols)
    col_idx = 0

    cols[col_idx].metric("보유 종목", f"{len(result)}개")
    col_idx += 1

    if not kr_stocks.empty:
        kr_cost = (kr_stocks["avg_price"] * kr_stocks["shares"]).sum()
        kr_value = (kr_stocks["current_price"] * kr_stocks["shares"]).sum()
        kr_profit = kr_value - kr_cost
        kr_return = kr_profit / kr_cost * 100
        cols[col_idx].metric("국내주식 수익률", f"{kr_return:+.2f}%", f"₩{kr_profit:+,.0f}")
        col_idx += 1

    if not us_stocks.empty:
        us_cost = (us_stocks["avg_price"] * us_stocks["shares"]).sum()
        us_value = (us_stocks["current_price"] * us_stocks["shares"]).sum()
        us_profit = us_value - us_cost
        us_return = us_profit / us_cost * 100
        cols[col_idx].metric("해외주식 수익률", f"{us_return:+.2f}%", f"${us_profit:+,.2f}")
        col_idx += 1

    overall_return = result["return_pct"].mean()
    cols[col_idx].metric("평균 수익률", f"{overall_return:+.2f}%")

    st.divider()

    # ---- 보유 종목 테이블 ----
    st.subheader("📋 보유 종목 현황")

    display_df = result.copy()
    display_df["수익률"] = display_df["return_pct"].apply(lambda x: f"{x:+.2f}%")
    display_df["손익"] = display_df.apply(
        lambda r: f"₩{r['profit_loss']:+,.0f}" if r['currency'] == "KRW" else f"${r['profit_loss']:+,.2f}",
        axis=1
    )
    display_df["현재가"] = display_df.apply(
        lambda r: f"₩{r['current_price']:,.0f}" if r['currency'] == "KRW" else f"${r['current_price']:,.2f}",
        axis=1
    )
    display_df["평균매수가_표시"] = display_df.apply(
        lambda r: f"₩{r['avg_price']:,.0f}" if r['currency'] == "KRW" else f"${r['avg_price']:,.2f}",
        axis=1
    )

    final_display = display_df[["name", "market", "ticker", "shares", "평균매수가_표시", "현재가", "수익률", "손익"]].rename(columns={
        "name": "종목명", "market": "시장", "ticker": "종목코드",
        "shares": "수량", "평균매수가_표시": "평균매수가"
    })
    st.dataframe(final_display, hide_index=True, use_container_width=True)

    st.divider()

    # ---- 차트 ----
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📊 종목별 수익률")
        fig_bar = px.bar(
            result,
            x="name",
            y="return_pct",
            color="return_pct",
            color_continuous_scale=["#ff4444", "#aaaaaa", "#00cc44"],
            color_continuous_midpoint=0,
            text=result["return_pct"].apply(lambda x: f"{x:+.2f}%"),
            labels={"name": "종목명", "return_pct": "수익률 (%)"}
        )
        fig_bar.update_traces(textposition='outside')
        fig_bar.update_layout(coloraxis_showscale=False, xaxis_title=None, yaxis_title="수익률 (%)")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("🥧 자산 비중")

        if not kr_stocks.empty and not us_stocks.empty:
            fig = make_subplots(
                rows=1, cols=2,
                specs=[[{"type": "pie"}, {"type": "pie"}]],
                subplot_titles=["국내주식 (KRW)", "해외주식 (USD)"]
            )
            fig.add_trace(go.Pie(
                labels=kr_stocks["name"].values,
                values=(kr_stocks["current_price"] * kr_stocks["shares"]).values,
                name="KR"
            ), 1, 1)
            fig.add_trace(go.Pie(
                labels=us_stocks["name"].values,
                values=(us_stocks["current_price"] * us_stocks["shares"]).values,
                name="US"
            ), 1, 2)
            st.plotly_chart(fig, use_container_width=True)
        else:
            market_stocks = kr_stocks if not kr_stocks.empty else us_stocks
            currency = "KRW" if not kr_stocks.empty else "USD"
            fig_pie = px.pie(
                values=(market_stocks["current_price"] * market_stocks["shares"]).values,
                names=market_stocks["name"].values,
                title=f"({currency})"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
