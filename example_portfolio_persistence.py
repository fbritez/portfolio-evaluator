from source.database import init_db
from source.model.portfolio import Portfolio



def crate_a_portfolio(ticker):
    from source.model.portfolio import Portfolio
    return Portfolio(name="Test Portfolio", tickers=["AAPL", "GOOGL", "MSFT"])
