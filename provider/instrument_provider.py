from typing import Optional, Dict, Any

import yfinance as yf


class InstrumentProvider:
    @staticmethod
    def obtener_info_financiera(ticker_symbol: str) -> Optional[Dict[str, Any]]:
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
                "Current Price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "Currency": info.get("currency"),
                "Market Capitalization": info.get("marketCap"),
                "52 Week High": info.get("fiftyTwoWeekHigh"),
                "52 Week Low": info.get("fiftyTwoWeekLow"),
                "P/E Ratio (Trailing)": info.get("trailingPE"),
                "Dividend Yield (%)": (info.get("dividendYield", 0) or 0) * 100,
            }

            print("=== FINANCIAL INSTRUMENT INFORMATION ===")
            for key, value in key_data.items():
                if isinstance(value, float):
                    print(f"{key}: {value:,.2f}")
                elif isinstance(value, int):
                    print(f"{key}: {value:,}")
                else:
                    print(f"{key}: {value}")

            return key_data

        except Exception as exc:
            print(f"Error while fetching ticker {ticker_symbol}: {exc}")
            return None
