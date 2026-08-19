import json
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "data"
DATABASE_PATH = DATABASE_DIR / "portfolio.db"


def get_connection():
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS portfolios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            tickers TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_portfolio(portfolio):
    from source.model.portfolio import Portfolio

    if not isinstance(portfolio, Portfolio):
        raise TypeError("Expected a Portfolio instance")

    conn = get_connection()
    conn.execute(
        """
        INSERT INTO portfolios (name, tickers)
        VALUES (?, ?)
        ON CONFLICT(name) DO UPDATE SET tickers = excluded.tickers
        """,
        (portfolio.name, json.dumps(portfolio.tickers)),
    )
    conn.commit()

    row = conn.execute(
        "SELECT id FROM portfolios WHERE name = ?",
        (portfolio.name,),
    ).fetchone()
    conn.close()

    portfolio.id = row["id"] if row else portfolio.id
    return portfolio


def load_portfolio(name):
    from source.model.portfolio import Portfolio

    conn = get_connection()
    row = conn.execute(
        "SELECT id, name, tickers FROM portfolios WHERE name = ?",
        (name,),
    ).fetchone()
    conn.close()

    if row is None:
        return None

    return Portfolio(
        tickers=json.loads(row["tickers"]),
        name=row["name"],
        portfolio_id=row["id"],
        lazy=True,
    )


def list_portfolios():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, name FROM portfolios ORDER BY id ASC"
    ).fetchall()
    conn.close()
    return [{"id": row["id"], "name": row["name"]} for row in rows]


def delete_portfolio(name):
    conn = get_connection()
    cursor = conn.execute(
        "DELETE FROM portfolios WHERE name = ?",
        (name,),
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0
