import streamlit as st
import pandas as pd
import yfinance as yf
import mplfinance as mpf
import requests
import os

def fetch_nse_stock_names(csv_path="stock_list.csv"):
    """
    Loads all stock names from a local CSV file.
    Returns a DataFrame of company names and symbols.
    """
    try:
        df = pd.read_csv(csv_path)
        return df[['NAME OF COMPANY', 'SYMBOL']]
    except Exception as e:
        st.error(f"Error loading local stock list: {e}")
        return pd.DataFrame(columns=['NAME OF COMPANY', 'SYMBOL'])

def fetch_chart_data(symbol, start_date="2024-01-01", end_date="2024-06-01"):
    """
    Fetch historical stock data using yfinance for the given symbol.
    """
    try:
        data = yf.download(f"{symbol}.NS", start=start_date, end=end_date, interval='1d')
        return data
    except Exception as e:
        st.error(f"Error fetching chart data: {e}")
        return pd.DataFrame()

def plot_candlestick(data, symbol):
    """
    Plot candlestick chart using mplfinance and display in Streamlit.
    """
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    mpf.plot(data, type='candle', style='charles', volume=True, ax=ax, title=f'{symbol} Candlestick Chart')
    st.pyplot(fig)

# Streamlit UI
st.title("NSE Stock Candlestick Viewer")
st.write("Select a stock to view its candlestick chart.")

stocks_df = fetch_nse_stock_names(csv_path="EQUITY_L.csv")
if not stocks_df.empty:
    stock_name = st.selectbox("Choose a stock:", stocks_df['NAME OF COMPANY'])
    symbol = stocks_df[stocks_df['NAME OF COMPANY'] == stock_name]['SYMBOL'].values[0]
    if st.button("Show Chart"):
        chart_data = fetch_chart_data(symbol)
        if not chart_data.empty:
            plot_candlestick(chart_data, symbol)
        else:
            st.warning("No chart data available for this stock.")
else:
    st.warning("Could not fetch stock list.")
