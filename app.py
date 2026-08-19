import logging

from source.database import get_backend_name
from source.server import create_app

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

app = create_app()


if __name__ == "__main__":
    logging.info("Starting application with %s database", get_backend_name())
    app.run(host="0.0.0.0", port=5000, debug=True)
