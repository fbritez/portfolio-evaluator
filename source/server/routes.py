from flask import Blueprint, jsonify, abort, request

from source.database import delete_portfolio as delete_portfolio_record
from source.database import list_portfolios, save_portfolio
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
    return jsonify(list_portfolios())


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
    portfolio = Portfolio.load(name)
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
            - tickers
          properties:
            name:
              type: string
              example: mi_portfolio
            tickers:
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
    tickers = payload.get("tickers") or []

    if not name:
        return jsonify({"error": "Portfolio name is required."}), 400

    if not isinstance(tickers, list) or not tickers:
        return jsonify({"error": "Portfolio tickers must be a non-empty list."}), 400

    portfolio = Portfolio(tickers=[str(t).upper() for t in tickers], name=str(name), lazy=True)
    saved = save_portfolio(portfolio)

    return jsonify({
        "id": saved.id,
        "name": saved.name,
        "tickers": saved.tickers,
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
    deleted = delete_portfolio_record(name)
    if not deleted:
        abort(404)
    return jsonify({"deleted": True, "name": name})


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
