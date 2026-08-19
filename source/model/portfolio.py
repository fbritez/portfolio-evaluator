import json

import pandas as pd

from provider.instrument_provider import InstrumentProvider


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

    def to_dict(self):
        evaluated = self.calculate_montly_valuation() if self.data is None else self._evaluated_portfolio
        if evaluated is None:
            evaluated = self.calculate_montly_valuation()

        enriched_instruments = []
        for instrument in self.instruments:
            details = InstrumentProvider.get_instrument_details(str(instrument).upper())
            enriched_instruments.append({
                "symbol": str(instrument).upper(),
                "details": details,
            })

        return {
            "id": self.id,
            "name": self.name,
            "instruments": enriched_instruments,
            "monthly_variation": evaluated.to_dict(orient="records") if isinstance(evaluated, pd.DataFrame) else evaluated,
        }

    def fetch_data(self):
        if not self.instruments:
            return pd.DataFrame()

        import yfinance as yf

        print("Getting quotations for the last month...")

        data = yf.download(self.instruments, period="1mo", progress=False)['Close']

        if isinstance(data, pd.Series):
            data = data.to_frame()

        return data

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
        import yfinance as yf

        if self.data is None:
            self.data = self.fetch_data()

        for instrument in self.instruments:
            if instrument not in self.data.columns:
                print(f"Getting data for {instrument}...")
                new_data = yf.download(instrument, period="1mo", progress=False)['Close']
                self.data[instrument] = new_data
        return self.data

    def get_sma200(self, ticker):
        import yfinance as yf

        df = yf.download(ticker, period="1y", progress=False)

        if isinstance(df, pd.Series):
            df = df.to_frame()

        if df.empty or len(df) < 200:
            print(f"Not enough data for {ticker}")
            return None

        df = df.copy()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()

        current_price = float(df['Close'].iloc[-1])
        sma_200 = float(df['SMA_200'].iloc[-1])

        return {
            "Ticker": ticker,
            "CurrentPrice": round(current_price, 2),
            "SMAA200": round(sma_200, 2),
            "Trend": "Bullish (above)" if current_price > sma_200 else "Bearish (below)"
        }

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
                    results.append({
                        "Ticker": instrument,
                        "PriceMonthAgo": round(initial_price, 2),
                        "CurrentPrice": round(current_price, 2),
                        "Variation": round(variation_pct, 2),
                        "SMA200": sma200.get("SMAA200") if sma200 else None,
                        "Trend": sma200.get("Trend") if sma200 else None
                    })
                else:
                    results.append({"Ticker": instrument, "Error": "Insufficient data"})
            else:
                results.append({"Ticker": instrument, "Error": "Ticker not found"})

        df = pd.DataFrame(results)
        if "Variation" in df.columns:
            df = df.sort_values(by="Variation", ascending=False, ignore_index=True)

        return df

    def calculate_montly_variation(self):
        return self.calculate_montly_valuation()
