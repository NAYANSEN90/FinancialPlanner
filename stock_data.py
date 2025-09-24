# Utility to get all stock symbols from EQUITY_L.csv
import pandas as pd
def get_all_stock_symbols():
    import os
    import warnings
    csv_path = "EQUITY_L.csv"
    if not os.path.exists(csv_path):
        warnings.warn(f"Stock list CSV not found: {csv_path}")
        return []
    stock_df = pd.read_csv(csv_path)
    if 'SYMBOL' not in stock_df.columns or stock_df.empty:
        warnings.warn(f"Stock list CSV is empty or missing SYMBOL column: {csv_path}")
        return []
    return stock_df['SYMBOL'].dropna().unique().tolist()
import yfinance as yf
import pandas as pd

_stock_data_cache = {}

def fetch_stock_chart_data(symbol, start_date="2024-01-01", end_date="2024-06-01", interval="1d"):
    """
    Fetch all available historical stock data for the given symbol and interval, cache it, and return only the data between start_date and end_date.
    The full history is kept in memory for backend use.
    """
    global _stock_data_cache
    cache_key = f"{symbol}_{interval}"
    try:
        if cache_key not in _stock_data_cache:
            # Fetch all available data from the first candle to today
            all_data = yf.download(f"{symbol}.NS", period="max", interval=interval, auto_adjust=False, multi_level_index=False)
            candlestick_df = all_data[["Open", "High", "Low", "Close", "Volume"]].copy()
            candlestick_df = candlestick_df.apply(pd.to_numeric, errors='coerce')
            candlestick_df = candlestick_df.dropna()
            _stock_data_cache[cache_key] = candlestick_df
        else:
            candlestick_df = _stock_data_cache[cache_key]
        # Filter for the requested period
        filtered_df = candlestick_df.loc[(candlestick_df.index >= pd.to_datetime(start_date)) & (candlestick_df.index <= pd.to_datetime(end_date))].copy()
        return filtered_df
    except Exception as e:
        print(f"Error fetching chart data: {e}")
        return pd.DataFrame()

if __name__ == "__main__":
    # Example: Test fetching data for RELIANCEs
    df = fetch_stock_chart_data("RELIANCE")
    print(df.head())
