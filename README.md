# Portfolio app with SQLite

This project exposes a list of tickers through a REST API and stores them in a local SQLite database.

Main endpoints:

- `GET /api/tickers` — returns the full ticker list in JSON.
- `GET /api/tickers/<symbol>` — checks whether a ticker exists.
- `GET /api/health` — health check.

Database:

- SQLite file: `data/portfolio.db`
- Tables:
  - `tickers`: list of tracked symbols
  - `prices`: historical close prices by ticker and date

Installation and execution:

```bash
python -m venv venv
venv\Scripts\activate   # Windows
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python app.py
```

The server will run at `http://0.0.0.0:5000`.

To initialize the database manually:

```python
from source.database import init_db
init_db()
```
