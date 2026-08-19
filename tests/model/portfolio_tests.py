import pandas as pd
import pytest
from unittest.mock import patch

from portfolio import Portfolio


def test_init():
    p = Portfolio(['AAPL', 'MSFT'])
    assert p.tickers == ['AAPL', 'MSFT']
    assert p.data is None


def test_save_ticker_new_and_existing():
    p = Portfolio(['AAPL'])
    res = p.save_ticker('MSFT')
    assert 'agregado' in res
    assert 'MSFT' in p.tickers

    res2 = p.save_ticker('MSFT')
    assert 'ya está' in res2
    assert p.tickers.count('MSFT') == 1


def test_fetch_data_with_dataframe():
    # prepare a fake DataFrame like yfinance returns
    dates = pd.date_range('2026-01-01', periods=3)
    df = pd.DataFrame({'AAPL': [1, 2, 3], 'MSFT': [4, 5, 6]}, index=dates)

    class FakeDF(dict):
        def __getitem__(self, key):
            return df

    p = Portfolio(['AAPL', 'MSFT'])

    with patch('yfinance.download', return_value={'Close': df}):
        p.fetch_data()

    assert isinstance(p.data, pd.DataFrame)
    assert list(p.data.columns) == ['AAPL', 'MSFT']


def test_fetch_data_with_series():
    # when a single ticker is requested, yfinance may return a Series
    s = pd.Series([10, 11, 12], index=pd.date_range('2026-01-01', periods=3), name='AAPL')

    p = Portfolio(['AAPL'])

    # yfinance.download(...)["Close"] will be a Series
    with patch('yfinance.download', return_value={'Close': s}):
        p.fetch_data()

    assert isinstance(p.data, pd.DataFrame)
    # after conversion, column name should be 'AAPL'
    assert 'AAPL' in p.data.columns


def test_refresh_data_adds_missing_ticker():
    # initial data has only AAPL
    dates = pd.date_range('2026-01-01', periods=3)
    df = pd.DataFrame({'AAPL': [1, 2, 3]}, index=dates)

    p = Portfolio(['AAPL', 'MSFT'])
    p.data = df.copy()

    # fake download for MSFT returns a Series
    s_msft = pd.Series([7, 8, 9], index=dates, name='MSFT')

    with patch('yfinance.download', return_value={'Close': s_msft}):
        updated = p.refresh_data()

    assert 'MSFT' in updated.columns
    assert list(updated['MSFT']) == [7, 8, 9]


def test_obtener_sma200_returns_summary():
    dates = pd.date_range('2026-01-01', periods=250)
    close = pd.Series(range(250, 0, -1), index=dates, name='Close')
    df = pd.DataFrame({'Close': close})

    p = Portfolio(['AAPL'])
    with patch('yfinance.download', return_value=df):
        result = p.obtener_sma200('AAPL')

    assert result['Ticker'] == 'AAPL'
    assert 'Precio Actual' in result
    assert 'SMA 200 Ruedas' in result
    assert result['Tendencia'] in {'Alcista (por encima)', 'Bajista (por debajo)'}


def test_calcular_variacion_mensual_returns_sorted_dataframe():
    dates = pd.date_range('2026-01-01', periods=5)
    data = pd.DataFrame({
        'AAPL': [100, 110, 120, 130, 150],
        'MSFT': [50, 48, 55, 60, 52],
    }, index=dates)

    p = Portfolio(['AAPL', 'MSFT'])

    with patch('yfinance.download', return_value={'Close': data}):
        result = p.calcular_variacion_mensual()

    assert list(result.columns)[:4] == ['Ticker', 'Precio Hace 1 Mes', 'Precio Actual', 'Variación (%)']
    assert set(result['Ticker']) == {'AAPL', 'MSFT'}
    assert result['Variación (%)'].iloc[0] >= result['Variación (%)'].iloc[1]
