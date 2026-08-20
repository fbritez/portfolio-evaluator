from functools import lru_cache

import pandas as pd
import yfinance as yf

from source.utils.logger import logger


class Analytics:
    @staticmethod
    @lru_cache(maxsize=512)
    def get_sma200(ticker):
        symbol = str(ticker).strip().upper()

        df = yf.download(symbol, period="1y", progress=False)

        if isinstance(df, pd.Series):
            df = df.to_frame()

        if df.empty or len(df) < 200:
            logger.info("Not enough data for %s", symbol)
            return None

        current_price = 0
        sma_200 = 0
        try:
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            current_price = float(df['Close'].iloc[-1])
            current_price = current_price if current_price is not None or current_price != 'nan' else 0
            sma_200 = float(df['SMA_200'].iloc[-1])
            sma_200 = sma_200 if sma_200 is not None or sma_200 != 'nan' else 0
        except Exception:
            logger.exception("Error occurred while calculating SMA_200 for %s", symbol)


        return {
            "Ticker": symbol,
            "CurrentPrice": round(current_price, 2),
            "SMAA200": round(sma_200, 2),
            "Trend": "Bullish (above)" if current_price > sma_200 else "Bearish (below)"
        }


    @staticmethod
    @lru_cache(maxsize=256)
    def calculate_rsi_for_symbol(symbol: str, periods: int = 14):
        symbol = str(symbol).strip().upper()
        df = yf.download(symbol, period="1y", progress=False)

        if isinstance(df, pd.Series):
            df = df.to_frame()

        delta = df['Close'].diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)

        average_gain = gains.ewm(alpha=1 / periods, adjust=False).mean()
        average_loss = losses.ewm(alpha=1 / periods, adjust=False).mean()

        rs = average_gain / average_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, periods: int = 14) -> pd.Series:
        if isinstance(df, pd.Series):
            df = df.to_frame()

        delta = df['Close'].diff()
        gains = delta.clip(lower=0)
        losses = -delta.clip(upper=0)

        average_gain = gains.ewm(alpha=1 / periods, adjust=False).mean()
        average_loss = losses.ewm(alpha=1 / periods, adjust=False).mean()

        rs = average_gain / average_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def fetch_history(instruments):
        if not instruments:
            return pd.DataFrame()

        logger.info("Getting quotations for the last month...")
        data = yf.download(list(instruments), period="1mo", progress=False)['Close']

        if isinstance(data, pd.Series):
            data = data.to_frame()

        return data

    @staticmethod
    def fetch_single_history(instrument):
        logger.info("Getting data for %s...", instrument)
        data = yf.download(instrument, period="1mo", progress=False)['Close']
        if isinstance(data, pd.Series):
            data = data.to_frame()
        return data

    @staticmethod
    @lru_cache(maxsize=256)
    def scan_instrument(symbol: str):
        logger.info('Calling %s', symbol)
        symbol = str(symbol).strip().upper()

        try:
            df = yf.download(symbol, period="1y", progress=False)

            if df.empty or len(df) < 200:
                logger.info("Not enough data for %s", symbol)
                return None

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['SMA_200'] = df['Close'].rolling(window=200).mean()
            df['RSI'] = Analytics.calculate_rsi_for_symbol(symbol, periods=14)

            today = df.iloc[-1]
            yesterday = df.iloc[-2]
            signals = []

            if yesterday['RSI'] <= 30 and today['RSI'] > 30:
                signals.append("RSI exiting oversold territory (cross above 30)")
            elif today['RSI'] <= 35:
                signals.append(f"RSI in low zone / oversold ({today['RSI']:.1f})")

            if yesterday['SMA_50'] <= yesterday['SMA_200'] and today['SMA_50'] > today['SMA_200']:
                signals.append("Golden cross (SMA 50 crosses above SMA 200)")

            if yesterday['Close'] <= yesterday['SMA_50'] and today['Close'] > today['SMA_50']:
                signals.append("Price breaking above SMA 50")

            if yesterday['Close'] <= yesterday['SMA_200'] and today['Close'] > today['SMA_200']:
                signals.append("Price recovering SMA 200")

            if not signals:
                logger.info('No significant signals detected for %s', symbol)
                return None

            return {
                "Ticker": symbol,
                "Price": float(today['Close']),
                "RSI": float(today['RSI']),
                "SMA_50": float(today['SMA_50']),
                "SMA_200": float(today['SMA_200']),
                "LongTermTrend": "Bullish" if today['Close'] > today['SMA_200'] else "Bearish",
                "DetectedSignals": signals,
            }
        except Exception:
            logger.exception("Error processing %s for technical analysis", symbol)
            return None
