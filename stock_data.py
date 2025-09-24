import yfinance as yf
import pandas as pd

def fetch_stock_chart_data(symbol, start_date="2024-01-01", end_date="2024-06-01", interval="1d"):
    """
    Fetch historical stock data using yfinance for the given symbol.
    Returns a DataFrame with columns: Open, High, Low, Close, Volume, etc.
    """
    try:
        data = yf.download(f"{symbol}.NS", start=start_date, end=end_date, interval=interval, multi_level_index=False)
        # Extract only candlestick columns
        print(data)
        candlestick_df = data[["Open", "High", "Low", "Close","Volume"]].copy()
        # Ensure all columns are numeric
        candlestick_df = candlestick_df.apply(pd.to_numeric, errors='coerce')
        # Drop rows with missing values
        candlestick_df = candlestick_df.dropna()
        return candlestick_df
    except Exception as e:
        print(f"Error fetching chart data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Example: Test fetching data for RELIANCEs
    df = fetch_stock_chart_data("RELIANCE")
    print(df.head())
