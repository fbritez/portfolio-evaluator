from typing import Optional, Dict, Any

import yfinance as yf


class InstrumentProvider:
    _cache: Dict[str, Optional[Dict[str, Any]]] = {}

    @staticmethod
    def get_instrument_details(ticker_symbol: str) -> Optional[Dict[str, Any]]:
        """
        Gets key metrics and information for a financial instrument given its ticker symbol.
        Uses a simple in-memory cache to avoid repeated Yahoo Finance calls for the same symbol.
        """
        normalized_symbol = str(ticker_symbol).strip().upper()
        if normalized_symbol in InstrumentProvider._cache:
            return InstrumentProvider._cache[normalized_symbol]

        ticker = yf.Ticker(normalized_symbol)

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

            InstrumentProvider._cache[normalized_symbol] = key_data
            return key_data

        except Exception as exc:
            print(f"Error while fetching ticker {ticker_symbol}: {exc}")
            InstrumentProvider._cache[normalized_symbol] = None
            return None
