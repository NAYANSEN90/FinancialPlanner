
import streamlit as st
import pandas as pd
import mplfinance as mpf
from stock_data import fetch_stock_chart_data

def prepare_mpf_data(data):
    """
    Clean and prepare DataFrame for mplfinance plotting.
    Ensures required columns, numeric types, datetime index, and no NaNs.
    Returns cleaned DataFrame or None if unsuitable.
    """
    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    df = data.copy()
    # Ensure index is datetime
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
    if not pd.api.types.is_datetime64_any_dtype(df.index):
        df.index = pd.to_datetime(df.index)
    # Only keep required columns
    df = df[required_cols]
    # Ensure all columns are numeric
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=required_cols)
    return df
    

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


def plot_candlestick(data, symbol):
    """
    Plot candlestick chart using mplfinance and display in Streamlit.
    """
    # Clean and prepare data for mplfinance
    cleaned = prepare_mpf_data(data)
    if cleaned is None or cleaned.empty:
        st.warning("Data is not suitable for candlestick plotting.")
        return
   
    # Use returnfig=True and do not pass ax
    fig, _ = mpf.plot(cleaned, type='candle', style='charles', volume=True, title=f'{symbol} Candlestick Chart', returnfig=True)
    st.pyplot(fig)



# Streamlit UI
st.set_page_config(layout="wide")
stocks_df = fetch_nse_stock_names(csv_path="EQUITY_L.csv")

# --- Defaults ---
import datetime
today = pd.Timestamp.today().normalize()
default_end = today
default_start = today - pd.DateOffset(years=1)
default_symbol = "RELIANCE"
default_interval = "1d"

# --- Session State for Watchlist and Chart Selection ---
if 'watchlist' not in st.session_state:
    st.session_state['watchlist'] = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
if 'selected_symbol' not in st.session_state:
    st.session_state['selected_symbol'] = default_symbol
if 'interval' not in st.session_state:
    st.session_state['interval'] = default_interval


# --- Top Toolbar: Chart Name Input and Interval ---
st.markdown("<div style='background-color:#f0f2f6;padding:10px 0 10px 0;margin-bottom:10px;'><h2 style='display:inline;margin-right:30px;'>NSE Stock Candlestick Viewer</h2>", unsafe_allow_html=True)
toolbar1_col1, toolbar1_col2 = st.columns([3,1])

# Callback to update chart_name_input when watchlist selection changes
def update_chart_name_from_watchlist():
    st.session_state['chart_name_input'] = st.session_state['selected_symbol']

with toolbar1_col1:
    chart_name = st.text_input("Chart Name (Symbol)", value=st.session_state['selected_symbol'], key="chart_name_input")
with toolbar1_col2:
    interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=["1d", "1wk", "1mo"].index(st.session_state['interval']), key="interval_select")
st.markdown("</div>", unsafe_allow_html=True)

# --- Main Layout: Chart Center, Watchlist Right ---
main_col, watch_col = st.columns([7,2])

with watch_col:
    st.header("Watchlist")
    # Add to watchlist
    new_watch = st.text_input("Add to Watchlist", "")
    if st.button("Add", key="add_watch") and new_watch and new_watch not in st.session_state['watchlist']:
        st.session_state['watchlist'].append(new_watch.upper())
    # Remove from watchlist
    remove_watch = st.selectbox("Remove from Watchlist", st.session_state['watchlist'], key="remove_watch")
    if st.button("Remove", key="remove_btn") and remove_watch in st.session_state['watchlist']:
        st.session_state['watchlist'].remove(remove_watch)
    # Select from watchlist
    selected_watch = st.radio(
        "Select Stock",
        st.session_state['watchlist'],
        index=st.session_state['watchlist'].index(st.session_state['selected_symbol']) if st.session_state['selected_symbol'] in st.session_state['watchlist'] else 0,
        key="watchlist_radio",
        on_change=update_chart_name_from_watchlist
    )
    # If watchlist selection changes, update selected_symbol
    if selected_watch != st.session_state['selected_symbol']:
        st.session_state['selected_symbol'] = selected_watch

# --- Bottom Toolbar: Date Range ---
st.markdown("<div style='background-color:#f0f2f6;padding:10px 0 10px 0;margin-top:10px;'><b>Select Date Range</b>", unsafe_allow_html=True)
toolbar2_col1, toolbar2_col2 = st.columns(2)
with toolbar2_col1:
    start_date = st.date_input("Start Date", default_start, key="start_date")
with toolbar2_col2:
    end_date = st.date_input("End Date", default_end, key="end_date")
st.markdown("</div>", unsafe_allow_html=True)

# --- Chart Display Logic ---
with main_col:
    st.subheader(f"Candlestick Chart: {st.session_state['selected_symbol']}")
    if st.button("Show Chart", key="show_chart_btn"):
        # Use chart_name input as the selected symbol
        symbol = st.session_state['chart_name_input'].upper()
        st.session_state['selected_symbol'] = symbol
        st.session_state['interval'] = st.session_state['interval_select'] if 'interval_select' in st.session_state else default_interval
        chart_data = fetch_stock_chart_data(symbol, start_date=start_date.strftime("%Y-%m-%d"), end_date=end_date.strftime("%Y-%m-%d"), interval=st.session_state['interval'])
        if not chart_data.empty:
            plot_candlestick(chart_data, symbol)
        else:
            st.warning("No chart data available for this stock.")
