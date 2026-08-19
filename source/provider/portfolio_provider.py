from __future__ import annotations

from typing import Optional, List, Dict, Any

from source.database import delete_portfolio as delete_portfolio_record
from source.database import list_portfolios as database_list_portfolios
from source.database import load_portfolio as database_load_portfolio
from source.database import save_portfolio as database_save_portfolio


class PortfolioProvider:
    @staticmethod
    def list_portfolios() -> List[Dict[str, Any]]:
        return database_list_portfolios()

    @staticmethod
    def get_by_name(name: str):
        return database_load_portfolio(name)

    @staticmethod
    def save(portfolio):
        return database_save_portfolio(portfolio)

    @staticmethod
    def delete(name: str) -> bool:
        return delete_portfolio_record(name)

    @staticmethod
    def exists(name: str) -> bool:
        return PortfolioProvider.get_by_name(name) is not None
