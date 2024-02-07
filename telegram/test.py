import yfinance as yf


ticker = yf.Ticker("AAPaafdL")
print(ticker.get_fast_info())
if "lastPrice" not in ticker.get_fast_info():
    print("error")
