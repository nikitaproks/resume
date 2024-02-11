import mplfinance as mpf
import yfinance as yf
from pandas import DataFrame
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


def plot_fig(history: DataFrame, ticker: str):
    apds = [
        mpf.make_addplot(history["SMA20"], color="blue", width=0.75),
        mpf.make_addplot(history["BB_upper"], color="green", width=0.75),
        mpf.make_addplot(history["BB_lower"], color="red", width=0.75),
        mpf.make_addplot(
            history["BB_percent"],
            panel=1,
            color="purple",
            width=0.75,
            ylabel="BBands%",
        ),
        mpf.make_addplot(
            history["RSI"], panel=2, color="purple", width=0.75, ylabel="RSI"
        ),
    ]

    mpf.plot(
        history,
        type="ohlc",
        volume=False,
        show_nontrading=True,
        figratio=(12, 8),
        title=f"{ticker} Stock Price",
        style="charles",
        addplot=apds,
    )


def get_stock_history(ticker):
    ticker = yf.Ticker(ticker)
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
    history["BB_percent"] = (history["Close"] - history["BB_lower"]) / (
        history["BB_upper"] - history["BB_lower"]
    )
    return history


ticker = "MSFT"
history = get_stock_history(ticker)
plot_fig(history, ticker)
