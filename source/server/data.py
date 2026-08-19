DEFAULT_TICKERS = [
    "AAPL",
    "AXP",
    "CL",
    "EEM",
    "EWJ",
    "EWZ",
    "GLD",
    "GOOGL",
    "GS",
    "IBM",
    "IEUR",
    "MELI",
    "META",
    "MSFT",
    "MU",
    "NU",
    "NVDA",
    "RACE",
    "SLV",
    "SPY",
    "UL",
    "V",
    "VALE",
    "VEA",
    "VIST",
    "WMT",
    "XLI",
    "XLV",
]


def get_all_tickers():
    return DEFAULT_TICKERS.copy()


def get_ticker_list():
    return get_all_tickers()


tickers = get_ticker_list()
