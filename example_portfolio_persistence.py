from source.database import init_db
from source.model.portfolio import Portfolio


if __name__ == "__main__":
    init_db()

    portfolio = Portfolio(
        tickers=["AAPL", "MSFT", "NVDA"],
        name="tech_portfolio",
    )

    portfolio.save()
    print("Portfolio saved")

    loaded = Portfolio.load("tech_portfolio")
    print(loaded.to_dict())
