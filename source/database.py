import json
import os
import sqlite3
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_DIR = BASE_DIR / "data"
DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL")


def get_backend_name():
    if DATABASE_URL and DATABASE_URL.startswith(("postgres://", "postgresql://", "postgresql+psycopg://")):
        return "postgres"
    return "sqlite"


def get_database_path():
    configured_path = os.getenv("PORTFOLIO_DB_PATH")
    candidates = []

    if configured_path:
        candidates.append(Path(configured_path))

    candidates.extend([
        DATABASE_DIR / "portfolio.db",
        Path(tempfile.gettempdir()) / "portfolio.db",
    ])

    for path in candidates:
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.touch(exist_ok=True)
            path.unlink(missing_ok=True)
            return path
        except (OSError, PermissionError):
            continue

    raise OSError("No writable directory is available for the SQLite database.")


DATABASE_PATH = get_database_path()


def get_connection():
    if get_backend_name() == "postgres":
        import psycopg

        conn = psycopg.connect(DATABASE_URL)
        conn.row_factory = psycopg.rows.dict_row
        return conn

    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    if get_backend_name() == "postgres":
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS portfolios (
                id SERIAL PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                tickers TEXT NOT NULL
            )
            """
        )
    else:
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
    if get_backend_name() == "postgres":
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO portfolios (name, tickers)
                VALUES (%s, %s)
                ON CONFLICT (name) DO UPDATE SET tickers = EXCLUDED.tickers
                """,
                (portfolio.name, json.dumps(portfolio.tickers)),
            )
            cursor.execute(
                "SELECT id FROM portfolios WHERE name = %s",
                (portfolio.name,),
            )
            row = cursor.fetchone()
        conn.commit()
    else:
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

    portfolio.id = row["id"] if row and isinstance(row, dict) else row[0] if row else portfolio.id
    return portfolio


def load_portfolio(name):
    from source.model.portfolio import Portfolio

    conn = get_connection()
    if get_backend_name() == "postgres":
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, tickers FROM portfolios WHERE name = %s",
                (name,),
            )
            row = cursor.fetchone()
    else:
        row = conn.execute(
            "SELECT id, name, tickers FROM portfolios WHERE name = ?",
            (name,),
        ).fetchone()
    conn.close()

    if row is None:
        return None

    data = row["tickers"] if isinstance(row, dict) else row[2]
    return Portfolio(
        tickers=json.loads(data),
        name=row["name"] if isinstance(row, dict) else row[1],
        portfolio_id=row["id"] if isinstance(row, dict) else row[0],
        lazy=True,
    )


def list_portfolios():
    conn = get_connection()
    if get_backend_name() == "postgres":
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name FROM portfolios ORDER BY id ASC")
            rows = cursor.fetchall()
    else:
        rows = conn.execute(
            "SELECT id, name FROM portfolios ORDER BY id ASC"
        ).fetchall()
    conn.close()
    if get_backend_name() == "postgres":
        return [{"id": row["id"], "name": row["name"]} for row in rows]
    return [{"id": row["id"], "name": row["name"]} for row in rows]


def delete_portfolio(name):
    conn = get_connection()
    if get_backend_name() == "postgres":
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM portfolios WHERE name = %s", (name,))
            deleted = cursor.rowcount > 0
        conn.commit()
    else:
        cursor = conn.execute(
            "DELETE FROM portfolios WHERE name = ?",
            (name,),
        )
        deleted = cursor.rowcount > 0
        conn.commit()
    conn.close()
    return deleted
