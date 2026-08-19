from typing import Optional, Dict, Any

import yfinance as yf


class InstrumentProvider:
    @staticmethod
    def get_instrument_details(ticker_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Gets key metrics and information for a financial instrument given its ticker symbol.
        """
        ticker = yf.Ticker(ticker_symbol)

        try:
            info = ticker.info

            key_data = {
                "Name": info.get("shortName") or info.get("longName"),
                "Symbol": info.get("symbol"),
                "Sector": info.get("sector", "N/A"),
                "Industry": info.get("industry", "N/A"),
                "CurrentPrice": info.get("currentPrice") or info.get("regularMarketPrice"),
                "Currency": info.get("currency"),
                "MarketCapitalization": info.get("marketCap"),
                "52WeekHigh": info.get("fiftyTwoWeekHigh"),
                "52WeekLow": info.get("fiftyTwoWeekLow"),
                "RatioTrailing": info.get("trailingPE"),
                "DividendYield": (info.get("dividendYield", 0) or 0) * 100,
            }

            return key_data

        except Exception as exc:
            print(f"Error while fetching ticker {ticker_symbol}: {exc}")
            return None
