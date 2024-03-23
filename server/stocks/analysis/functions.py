import io

import mplfinance as mpf
import yfinance as yf
from django.db.models import Q
from pandas import DataFrame
from stocks.models import State, Subscription
from technical_analysis import moving_average


def calculate_bollinger_bands(close, window_size=20, num_of_std=2):
    # Calculate the moving average (middle band)
    sma = close.rolling(window=window_size).mean()

    # Calculate the standard deviation
    std_dev = close.rolling(window=window_size).std()

    # Calculate the upper and lower bands
    upper = sma + (std_dev * num_of_std)
    lower = sma - (std_dev * num_of_std)

    return (lower, sma, upper)


def rma(series, period):
    """Calculate the Running Moving Average (RMA) equivalent to TradingView's method."""
    alpha = 1 / period
    return series.ewm(alpha=alpha, adjust=False).mean()


def rsi(data, period=14):
    """Calculate the Relative Strength Index (RSI) similar to TradingView's calculation."""
    # Calculate price changes
    delta = data.diff()

    # Separate gains and losses
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    # Calculate the RMA for gains and losses
    rma_gains = rma(gains, period)
    rma_losses = rma(losses, period)

    # Calculate the Relative Strength (RS)
    rs = rma_gains / rma_losses

    # Calculate the RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi


def get_fig_buffer(history: DataFrame, symbol: str) -> io.BytesIO:
    apds = [
        mpf.make_addplot(history["SMA20"], color="blue", width=0.75),
        mpf.make_addplot(history["BB_upper"], color="green", width=0.75),
        mpf.make_addplot(history["BB_lower"], color="red", width=0.75),
        mpf.make_addplot(
            history["BBands%"],
            panel=1,
            color="green",
            width=0.75,
            ylabel="BBands%",
        ),
        mpf.make_addplot(
            history["RSI"], panel=2, color="purple", width=0.75, ylabel="RSI"
        ),
        mpf.make_addplot(
            history["RSI_SMA14"],
            panel=2,
            color="yellow",
            width=0.75,
            ylabel="RSI",
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


def get_stock_history(subscription: Subscription) -> DataFrame:
    ticker = yf.Ticker(subscription.stock.ticker)
    history = ticker.history(
        period=subscription.period,
        interval=subscription.interval,
    )

    history["RSI"] = rsi(history["Close"], 14)
    history["RSI_SMA14"] = moving_average.sma(history["RSI"], 14)
    (
        history["BB_lower"],
        history["SMA20"],
        history["BB_upper"],
    ) = calculate_bollinger_bands(history["Close"])
    history["BBands%"] = (history["Close"] - history["BB_lower"]) / (
        history["BB_upper"] - history["BB_lower"]
    )
    return history


def analyse_stock(current_bb_percent: float) -> State:
    states_with_either_condition = State.objects.filter(
        Q(
            stateindicator__indicator__name="BBands%",
            stateindicator__lower_threshold__lte=current_bb_percent,
            stateindicator__upper_threshold__gt=current_bb_percent,
        )
    )

    if states_with_either_condition.count() == 0:
        return State.objects.get(name="Hold")

    return states_with_either_condition.first()  # type: ignore
