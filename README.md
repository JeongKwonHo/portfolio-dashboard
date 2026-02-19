# 📈 포트폴리오 수익률 추적기

국내/해외 주식 보유 종목의 현재 시세를 실시간으로 조회하고 수익률을 추적하는 Streamlit 웹 앱입니다.

## 주요 기능

- 한국(KRX) / 미국(NYSE, NASDAQ) 주식 종목 추가 및 관리
- 실시간 시세 조회 (한국: pykrx, 미국: yfinance)
- 종목별 수익률 및 손익 계산
- 국내/해외 포트폴리오 요약 지표
- 종목별 수익률 막대 차트 및 자산 비중 파이 차트

## 실행 방법

```bash
# 패키지 설치
pip install -r requirements.txt

# 앱 실행
python3 -m streamlit run app.py
```

브라우저에서 http://localhost:8501 접속

## 사용 방법

1. 왼쪽 사이드바에서 시장(KR/US) 선택
2. 종목코드, 종목명, 보유 수량, 평균 매수가 입력
3. **추가하기** 클릭 → 실시간 시세 조회 및 수익률 자동 계산

| 시장 | 종목코드 예시 |
|------|-------------|
| 한국 (KR) | 005930 (삼성전자), 013580 (계룡건설) |
| 미국 (US) | AAPL, TSLA, NVDA |

## 기술 스택

- [Streamlit](https://streamlit.io/) - 웹 UI
- [pykrx](https://github.com/sharebook-kr/pykrx) - 한국 주식 시세
- [yfinance](https://github.com/ranaroussi/yfinance) - 미국 주식 시세
- [Plotly](https://plotly.com/) - 차트
- [pandas](https://pandas.pydata.org/) - 데이터 처리
