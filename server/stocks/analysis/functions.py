import io

import mplfinance as mpf
import yfinance as yf
from django.db.models import Q
from pandas import DataFrame
from stocks.models import State, Stock
from technical_analysis import indicators


def calculate_bollinger_bands(close, window_size=20, num_of_std=2):
    # Calculate the moving average (middle band)
    sma = close.rolling(window=window_size).mean()

    # Calculate the standard deviation
    std_dev = close.rolling(window=window_size).std()

    # Calculate the upper and lower bands
    upper = sma + (std_dev * num_of_std)
    lower = sma - (std_dev * num_of_std)

    return (lower, sma, upper)


def get_fig_buffer(history: DataFrame, symbol: str) -> io.BytesIO:
    apds = [
        mpf.make_addplot(history["SMA20"], color="blue", width=0.75),
        mpf.make_addplot(history["BB_upper"], color="green", width=0.75),
        mpf.make_addplot(history["BB_lower"], color="red", width=0.75),
        mpf.make_addplot(
            history["BBands%"],
            panel=1,
            color="purple",
            width=0.75,
            ylabel="BBands%",
        ),
        mpf.make_addplot(
            history["RSI"], panel=2, color="purple", width=0.75, ylabel="RSI"
        ),
    ]

    buffer = io.BytesIO()
    mpf.plot(
        history,
        type="ohlc",
        volume=False,
        show_nontrading=True,
        figratio=(12, 8),
        title=f"{symbol} Stock Price",
        style="charles",
        addplot=apds,
        savefig=buffer,
    )
    buffer.seek(0)

    return buffer


def get_stock_history(stock: Stock):
    ticker = yf.Ticker(stock.ticker)
    history = ticker.history(
        period="6mo",
        interval="1d",
    )

    history["RSI"] = indicators.rsi(history["Close"], period=14)
    (
        history["BB_lower"],
        history["SMA20"],
        history["BB_upper"],
    ) = calculate_bollinger_bands(history["Close"])
    history["BBands%"] = (history["Close"] - history["BB_lower"]) / (
        history["BB_upper"] - history["BB_lower"]
    )
    return history


def analyse_stock(current_rsi: float, current_bb_percent: float) -> str:
    states_with_either_condition = State.objects.filter(
        Q(
            stateindicator__indicator__name="RSI",
            stateindicator__lower_threshold__lte=current_rsi,
            stateindicator__upper_threshold__gt=current_rsi,
        )
        | Q(
            stateindicator__indicator__name="BBands%",
            stateindicator__lower_threshold__lte=current_bb_percent,
            stateindicator__upper_threshold__gt=current_bb_percent,
        )
    ).distinct()

    return states_with_either_condition.first()
