# tool_hub/stock_tool.py
import json
import yfinance as yf
from qwen_agent.tools.base import BaseTool, register_tool

@register_tool('stock_price_checker')
class StockPriceChecker(BaseTool):
    description = (
        '주식 티커(ticker)를 입력받아 현재 주식 가격과 관련 정보를 실시간으로 조회합니다. '
        '한국 주식은 티커 뒤에 .KS (코스피) 또는 .KQ (코스닥)를 붙여야 합니다.'
    )
    parameters = [{
        'name': 'ticker',
        'type': 'string',
        'description': '조회할 주식의 티커 심볼. 예: 삼성전자는 "005930.KS", 애플은 "AAPL"',
        'required': True
    }]

    def call(self, params: str, **kwargs) -> str:
        try:
            ticker_symbol = self._parse_params(params).get('ticker')
            if not ticker_symbol:
                return json.dumps({'error': '티커(ticker)를 입력해야 합니다.'})

            stock = yf.Ticker(ticker_symbol)
            # get_info()는 더 많은 정보를 가져오지만, 속도를 위해 fast_info 사용
            info = stock.fast_info

            if not info or 'lastPrice' not in info:
                 return json.dumps({'error': f"'{ticker_symbol}'에 대한 정보를 찾을 수 없습니다. 티커가 정확한지 확인하세요."})

            result = {
                "ticker": ticker_symbol,
                "companyName": info.get('longName', 'N/A'),
                "currentPrice": info.get('lastPrice'),
                "currency": info.get('currency'),
                "dayHigh": info.get('dayHigh'),
                "dayLow": info.get('dayLow'),
            }
            return json.dumps(result, ensure_ascii=False)

        except Exception as e:
            return json.dumps({'error': f'주식 정보 조회 중 오류 발생: {str(e)}'}, ensure_ascii=False)