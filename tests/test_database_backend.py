import importlib


def test_database_backend_prefers_postgres_url(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://user:pass@host:5432/app")
    import source.database as database
    importlib.reload(database)

    assert database.get_backend_name() == "postgres"
    assert database.DATABASE_URL == "postgresql://user:pass@host:5432/app"
