from source.database import init_db

if __name__ == "__main__":
    init_db()
    print("SQLite database initialized at data/portfolio.db")
