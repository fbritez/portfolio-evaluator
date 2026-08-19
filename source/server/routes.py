from flask import Blueprint, jsonify, abort, request

from provider.instrument_provider import InstrumentProvider
from provider.portfolio_provider import PortfolioProvider
from source.model.portfolio import Portfolio
from .data import tickers

bp = Blueprint("api", __name__)


@bp.route("/tickers", methods=["GET"])
def get_tickers():
    """
    List available tickers
    ---
    responses:
      200:
        description: A list of tickers
    """
    return jsonify(tickers)


@bp.route("/tickers/<symbol>", methods=["GET"])
def get_ticker(symbol):
    """
    Get a ticker by symbol
    ---
    parameters:
      - name: symbol
        in: path
        type: string
        required: true
    responses:
      200:
        description: Ticker found
      404:
        description: Ticker not found
    """
    symbol = symbol.upper()
    if symbol in tickers:
        return jsonify({"symbol": symbol})
    abort(404)


@bp.route("/portfolios", methods=["GET"])
def get_portfolios():
    """
    List all saved portfolios
    ---
    responses:
      200:
        description: Portfolio list
    """
    return jsonify(PortfolioProvider.list_portfolios())


@bp.route("/portfolios/<name>", methods=["GET"])
def get_portfolio_by_name(name):
    """
    Get a portfolio by name
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
    responses:
      200:
        description: Portfolio loaded
      404:
        description: Portfolio not found
    """
    portfolio = PortfolioProvider.get_by_name(name)
    if portfolio is None:
        abort(404)

    portfolio.data = portfolio.fetch_data()
    portfolio._evaluated_portfolio = portfolio.calculate_montly_variation()
    return jsonify(portfolio.to_dict())


@bp.route("/portfolios", methods=["POST"])
def create_portfolio():
    """
    Save or update a portfolio
    ---
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - instruments
          properties:
            name:
              type: string
              example: mi_portfolio
            instruments:
              type: array
              items:
                type: string
              example: ["AAPL", "MSFT", "NVDA"]
    responses:
      201:
        description: Portfolio saved successfully
      400:
        description: Invalid payload
    """
    payload = request.get_json(silent=True) or {}

    name = payload.get("name")
    instruments = payload.get("instruments") or payload.get("tickers") or []

    if not name:
        return jsonify({"error": "Portfolio name is required."}), 400

    clean_name = str(name).strip()
    if not clean_name:
        return jsonify({"error": "Portfolio name is required."}), 400

    if not isinstance(instruments, list) or not instruments:
        return jsonify({"error": "Portfolio instruments must be a non-empty list."}), 400

    portfolio = Portfolio(instruments=[str(t).upper() for t in instruments], name=clean_name, lazy=True)
    saved = PortfolioProvider.save(portfolio)

    return jsonify({
        "id": saved.id,
        "name": saved.name,
        "instruments": saved.instruments,
        "tickers": saved.instruments,
    }), 201


@bp.route("/portfolios/empty/<name>", methods=["POST"])
def create_empty_portfolio(name):
    """
    Create an empty portfolio by name
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
    responses:
      201:
        description: Empty portfolio created successfully
      400:
        description: Invalid name
    """
    clean_name = str(name).strip()
    if not clean_name:
        return jsonify({"error": "Portfolio name is required."}), 400

    existing = PortfolioProvider.get_by_name(clean_name)
    if existing is not None:
        return jsonify({"error": f"Portfolio '{clean_name}' already exists."}), 409

    portfolio = Portfolio(instruments=[], name=clean_name, lazy=True)
    saved = PortfolioProvider.save(portfolio)

    return jsonify({
        "id": saved.id,
        "name": saved.name,
        "instruments": saved.instruments,
        "tickers": saved.instruments,
    }), 201


@bp.route("/portfolios/<name>", methods=["DELETE"])
def delete_portfolio(name):
    """
    Delete a portfolio by name
    ---
    parameters:
      - name: name
        in: path
        type: string
        required: true
    responses:
      200:
        description: Portfolio deleted
      404:
        description: Portfolio not found
    """
    deleted = PortfolioProvider.delete(name)
    if not deleted:
        abort(404)
    return jsonify({"deleted": True, "name": name})


@bp.route("/searchInstrument/<ticker>", methods=["GET"])
def search_instrument(ticker):
    """
    Get financial details for a ticker symbol
    ---
    parameters:
      - name: ticker
        in: path
        type: string
        required: true
    responses:
      200:
        description: Instrument details returned successfully
      404:
        description: Instrument not found
    """
    ticker_symbol = str(ticker).strip().upper()
    if not ticker_symbol:
        return jsonify({"error": "Ticker is required."}), 400

    details = InstrumentProvider.get_instrument_details(ticker_symbol)
    if details is None:
        return jsonify({"error": "Instrument not found or unavailable."}), 404

    return jsonify(details)


@bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check
    ---
    responses:
      200:
        description: API healthy
    """
    return jsonify({"status": "ok"})
