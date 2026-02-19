import pandas as pd


def calculate_portfolio(portfolio_df: pd.DataFrame) -> pd.DataFrame:
    """각 보유 종목의 수익률을 계산합니다."""
    df = portfolio_df.copy()

    # 시세 조회 실패한 종목 제외
    df = df.dropna(subset=['current_price'])

    if df.empty:
        return df

    df['profit_loss'] = (df['current_price'] - df['avg_price']) * df['shares']
    df['return_pct'] = (df['current_price'] - df['avg_price']) / df['avg_price'] * 100
    df['total_cost'] = df['avg_price'] * df['shares']
    df['current_value'] = df['current_price'] * df['shares']

    return df
