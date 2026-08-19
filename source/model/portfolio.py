import logging

import pandas as pd

from analitics import Analytics
from provider.instrument_provider import InstrumentProvider

logger = logging.getLogger(__name__)


class Portfolio:
    def __init__(self, instruments=None, name="default", portfolio_id=None, lazy=False, **kwargs):
        tickers = kwargs.pop("tickers", None)
        if tickers is not None and instruments is None:
            instruments = tickers

        self.id = portfolio_id
        self.name = name
        self.instruments = instruments or []
        self.tickers = self.instruments

        if lazy:
            self.data = None
            self._evaluated_portfolio = None
        else:
            self.data = self.fetch_data()
            self._evaluated_portfolio = self.calculate_montly_valuation()

    def save(self):
        from provider.portfolio_provider import PortfolioProvider

        return PortfolioProvider.save(self)

    @classmethod
    def load(cls, name):
        from provider.portfolio_provider import PortfolioProvider

        return PortfolioProvider.get_by_name(name)

    def to_dict(self, simple=False):
        if simple:
            return {
                "id": self.id,
                "name": self.name,
                "instruments": self._get_enriched_instruments(),
            }
        else:
            return self._heavy_detailed_dict()

    def _heavy_detailed_dict(self):
        evaluated = self.calculate_montly_valuation() if self.data is None else self._evaluated_portfolio
        if evaluated is None:
            evaluated = self.calculate_montly_valuation()

        return {
            "id": self.id,
            "name": self.name,
            "instruments": self._get_enriched_instruments(),
            "technical_analysis": self.get_technical_analysis(),
            "monthly_variation": evaluated.to_dict(orient="records") if isinstance(evaluated, pd.DataFrame) else evaluated,
        }

    def _get_enriched_instruments(self):
        enriched_instruments = []
        for instrument in self.instruments:
            details = InstrumentProvider.get_instrument_details(str(instrument).upper())
            enriched_instruments.append({
                "symbol": str(instrument).upper(),
                "details": details,
            })
        return enriched_instruments

    def fetch_data(self):
        return Analytics.fetch_history(self.instruments)

    def save_instrument(self, a_ticker):
        if a_ticker not in self.instruments:
            self.instruments.append(a_ticker)
            self.tickers = self.instruments
            status = f"Ticker {a_ticker} added to the portfolio."
        else:
            status = f"Ticker {a_ticker} is already in the portfolio."

        return status

    def save_ticker(self, a_ticker):
        return self.save_instrument(a_ticker)

    def refresh_data(self):
        if self.data is None:
            self.data = self.fetch_data()

        for instrument in self.instruments:
            if instrument not in self.data.columns:
                new_data = Analytics.fetch_single_history(instrument)
                self.data[instrument] = new_data
        return self.data

    def scan_instrument(self, symbol: str):
        return Analytics.scan_instrument(symbol)

    def get_technical_analysis(self):
        if not self.instruments:
            return []

        results = []
        for instrument in self.instruments:
            signal = self.scan_instrument(str(instrument).upper())
            if signal is not None and signal.get("DetectedSignals"):
                results.append(signal)
        return results

    def scan_market(self, instruments=None):
        instruments = instruments or self.instruments
        results = []

        logger.info("Starting scan of %s instruments...", len(instruments))

        for instrument in instruments:
            result = self.scan_instrument(str(instrument).upper())
            if result and result.get("DetectedSignals"):
                results.append({
                    "Ticker": result["Ticker"],
                    "Price ($)": round(result["Price"], 2),
                    "RSI": round(result["RSI"], 1),
                    "SMA_50": round(result["SMA_50"], 2),
                    "SMA_200": round(result["SMA_200"], 2),
                    "Trend": result["LongTermTrend"],
                    "Signals": " | ".join(result["DetectedSignals"]),
                })

        if not results:
            logger.info("No active buy signals were found in the selected list.")
            return pd.DataFrame()

        return pd.DataFrame(results)

    def get_sma200(self, ticker):
        return Analytics.get_sma200(ticker)

    def calculate_montly_valuation(self):
        if not self.instruments:
            return pd.DataFrame(columns=["Ticker", "PriceMonthAgo", "CurrentPrice", "Variation", "SMA200", "Trend"])

        if self.data is None:
            self.data = self.fetch_data()

        data = self.data.copy()

        if isinstance(data, pd.Series):
            data = data.to_frame()

        results = []

        for instrument in self.instruments:
            if instrument in data.columns:
                prices = data[instrument].dropna()

                if len(prices) >= 2:
                    initial_price = prices.iloc[0]
                    current_price = prices.iloc[-1]
                    variation_pct = ((current_price - initial_price) / initial_price) * 100
                    sma200 = self.get_sma200(instrument)
                    print('Que mierda hay aca', sma200)
                    results.append({
                        "Ticker": instrument,
                        "PriceMonthAgo": round(initial_price, 2),
                        "CurrentPrice": round(current_price, 2),
                        "Variation": round(variation_pct, 2),
                        "SMA200": sma200.get("SMAA200") if sma200 else 0,
                        "Trend": sma200.get("Trend") if sma200 else 0
                    })
                else:
                    results.append({"Ticker": instrument, "Error": "Insufficient data"})
            else:
                results.append({"Ticker": instrument, "Error": "Ticker not found"})

        df = pd.DataFrame(results)
        if "Variation" in df.columns:
            df = df.sort_values(by="Variation", ascending=False, ignore_index=True)

        return df
