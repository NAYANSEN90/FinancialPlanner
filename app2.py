import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from stock_data import fetch_stock_chart_data

st.set_page_config(layout="wide")

# --- Defaults ---
import datetime
today = pd.Timestamp.today().normalize()
default_end = today
default_start = today - pd.DateOffset(years=1)
default_symbol = "RELIANCE"
default_interval = "1d"

# --- Session State for EMA and Chart ---
if 'ema_list' not in st.session_state:
    st.session_state['ema_list'] = [{'period': 20, 'visible': True}]
if 'selected_symbol' not in st.session_state:
    st.session_state['selected_symbol'] = default_symbol
if 'interval' not in st.session_state:
    st.session_state['interval'] = default_interval

# --- Indicator Section: EMA controls ---
st.markdown("<div style='background-color:#e3e6ea;padding:10px 0 10px 0;margin-bottom:10px;'><b>Indicators: Exponential Moving Average (EMA)</b>", unsafe_allow_html=True)
ema_cols = st.columns([2,2,2,2,2])
for i, ema in enumerate(st.session_state['ema_list']):
    with ema_cols[i % 5]:
        st.session_state['ema_list'][i]['period'] = st.number_input(f"EMA {i+1} Period", min_value=1, max_value=200, value=ema['period'], key=f"ema_period_{i}")
        st.session_state['ema_list'][i]['visible'] = st.checkbox(f"Show EMA {i+1}", value=ema['visible'], key=f"ema_visible_{i}")
def add_ema_callback():
    st.session_state['ema_list'].append({'period': 20, 'visible': True})
    st.session_state['show_chart_auto2'] = True

def remove_ema_callback():
    if len(st.session_state['ema_list']) > 1:
        st.session_state['ema_list'].pop()
        st.session_state['show_chart_auto2'] = True

add_ema = st.button("Add EMA", key="add_ema_btn", on_click=add_ema_callback)
remove_ema = st.button("Remove Last EMA", key="remove_ema_btn", on_click=remove_ema_callback)
def on_ema_change():
    st.session_state['show_chart_auto2'] = True

for i, ema in enumerate(st.session_state['ema_list']):
    unique_key = f"{i}_{id(ema)}"
    st.session_state['ema_list'][i]['period'] = st.number_input(
        f"EMA {i+1} Period", min_value=1, max_value=200, value=ema['period'], key=f"ema_period_{unique_key}", on_change=on_ema_change)
    st.session_state['ema_list'][i]['visible'] = st.checkbox(
        f"Show EMA {i+1}", value=ema['visible'], key=f"ema_visible_{unique_key}", on_change=on_ema_change)
st.markdown("</div>", unsafe_allow_html=True)


# --- Top Toolbar: Symbol autocomplete, interval, show chart ---
st.markdown("<div style='background-color:#f0f2f6;padding:10px 0 10px 0;margin-bottom:10px;'><h2 style='display:inline;margin-right:30px;'>NSE Stock Candlestick Viewer (Plotly)</h2>", unsafe_allow_html=True)
toolbar1_col1, toolbar1_col2 = st.columns([3,1])
with toolbar1_col1:
    import pandas as pd
    # Load stock list from CSV (symbol and name)
    stock_df = pd.read_csv("EQUITY_L.csv")
    stock_options = [f"{row['SYMBOL']} - {row['NAME OF COMPANY']}" for _, row in stock_df.iterrows()]
    # Autocomplete selectbox
    selected_stock = st.selectbox(
        "Chart Name (Symbol)",
        options=stock_options,
        index=stock_options.index(f"{st.session_state['selected_symbol']} - " + stock_df.loc[stock_df['SYMBOL'] == st.session_state['selected_symbol'], 'NAME OF COMPANY'].values[0]) if st.session_state['selected_symbol'] in stock_df['SYMBOL'].values else 0,
        key="chart_name_select2"
    )
    # Extract symbol from selection
    symbol = selected_stock.split(" - ")[0]
    st.session_state['selected_symbol'] = symbol
with toolbar1_col2:
    def on_interval_change():
        st.session_state['show_chart_auto2'] = True
        st.session_state['interval'] = st.session_state['interval_select2']
    interval = st.selectbox(
        "Interval",
        ["1d", "1wk", "1mo"],
        index=["1d", "1wk", "1mo"].index(st.session_state['interval']),
        key="interval_select2",
        on_change=on_interval_change
    )
st.markdown("</div>", unsafe_allow_html=True)

# --- Date Range ---
st.markdown("<div style='background-color:#f0f2f6;padding:10px 0 10px 0;margin-top:10px;'><b>Select Date Range</b>", unsafe_allow_html=True)
toolbar2_col1, toolbar2_col2 = st.columns(2)
with toolbar2_col1:
    start_date = st.date_input("Start Date", default_start, key="start_date2")
with toolbar2_col2:
    end_date = st.date_input("End Date", default_end, key="end_date2")
st.markdown("</div>", unsafe_allow_html=True)

import numpy as np

# --- Pivot High/Low Toggle ---
st.markdown("<div style='background-color:#e3e6ea;padding:10px 0 10px 0;margin-bottom:10px;'><b>Technical Analysis: Pivots</b>", unsafe_allow_html=True)
pivot_col1, pivot_col2 = st.columns(2)
with pivot_col1:
    show_pivot_highs = st.checkbox("Show Pivot Highs", value=False, key="show_pivot_highs")
with pivot_col2:
    show_pivot_lows = st.checkbox("Show Pivot Lows", value=False, key="show_pivot_lows")
st.markdown("</div>", unsafe_allow_html=True)

if 'show_chart_auto2' not in st.session_state:
    st.session_state['show_chart_auto2'] = False
show_chart = st.button("Show Chart (Plotly)", key="show_chart_btn2")
if st.session_state['show_chart_auto2']:
    show_chart = True
    st.session_state['show_chart_auto2'] = False
if show_chart:
    # Fetch both full history and filtered data
    from stock_data import _stock_data_cache
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    chart_data = fetch_stock_chart_data(symbol, start_date=start_str, end_date=end_str, interval=interval)
    # Get full history from cache
    cache_key = f"{symbol}_{interval}"
    full_data = _stock_data_cache.get(cache_key, chart_data)

    # --- Sliding window logic for max 20,000 candles ---
    MAX_CANDLES = 20000
    if 'window_start_idx' not in st.session_state:
        st.session_state['window_start_idx'] = 0
    # Only apply sliding window if chart_data is too large
    if len(chart_data) > MAX_CANDLES:
        # Set up navigation buttons
        window_start = st.session_state['window_start_idx']
        window_end = window_start + MAX_CANDLES
        if window_end > len(chart_data):
            window_end = len(chart_data)
            window_start = window_end - MAX_CANDLES
        # Navigation controls
        nav_col1, nav_col2, nav_col3 = st.columns([1,2,1])
        with nav_col1:
            if st.button('← Older', key='older_candles'):
                st.session_state['window_start_idx'] = max(0, window_start - MAX_CANDLES//2)
        with nav_col3:
            if st.button('Newer →', key='newer_candles'):
                st.session_state['window_start_idx'] = min(len(chart_data) - MAX_CANDLES, window_start + MAX_CANDLES//2)
        chart_data_window = chart_data.iloc[window_start:window_end]
    else:
        chart_data_window = chart_data
        st.session_state['window_start_idx'] = 0

    if not chart_data_window.empty:
        # --- Find Pivot Highs/Lows ---
        def find_pivots(series, window=3, mode='high'):
            pivots = []
            for i in range(window, len(series)-window):
                if mode == 'high':
                    if series[i] == max(series[i-window:i+window+1]):
                        pivots.append(i)
                else:
                    if series[i] == min(series[i-window:i+window+1]):
                        pivots.append(i)
            return pivots

        fig = go.Figure()
        # Candlestick
        fig.add_trace(go.Candlestick(
            x=chart_data_window.index,
            open=chart_data_window['Open'],
            high=chart_data_window['High'],
            low=chart_data_window['Low'],
            close=chart_data_window['Close'],
            name='Candlestick'))
        # Volume (secondary y)
        fig.add_trace(go.Bar(
            x=chart_data_window.index,
            y=chart_data_window['Volume'],
            name='Volume',
            marker_color='rgba(50,50,150,0.7)',
            yaxis='y2',
            opacity=0.4
        ))
        # EMA overlays (use full history, plot only visible period)
        color_cycle = ['#e377c2', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        for i, ema in enumerate(st.session_state['ema_list']):
            if ema['visible']:
                ema_series_full = full_data['Close'].ewm(span=ema['period'], adjust=False).mean()
                ema_series = ema_series_full.loc[chart_data_window.index]
                fig.add_trace(go.Scatter(
                    x=chart_data_window.index,
                    y=ema_series,
                    mode='lines',
                    name=f'EMA {ema["period"]}',
                    line=dict(color=color_cycle[i % len(color_cycle)], width=2)
                ))
        # Mark Pivot Highs/Lows
        pivot_marker_size = 16
        pivot_high_indices = find_pivots(chart_data_window['High'], window=3, mode='high') if show_pivot_highs else []
        pivot_low_indices = find_pivots(chart_data_window['Low'], window=3, mode='low') if show_pivot_lows else []
        if show_pivot_highs:
            fig.add_trace(go.Scatter(
                x=chart_data_window.index[pivot_high_indices],
                y=chart_data_window['High'].iloc[pivot_high_indices],
                mode='markers',
                marker=dict(symbol='triangle-up', color='red', size=pivot_marker_size),
                name='Pivot High',
                hoverinfo='x+y+name'
            ))
        if show_pivot_lows:
            fig.add_trace(go.Scatter(
                x=chart_data_window.index[pivot_low_indices],
                y=chart_data_window['Low'].iloc[pivot_low_indices],
                mode='markers',
                marker=dict(symbol='triangle-down', color='green', size=pivot_marker_size),
                name='Pivot Low',
                hoverinfo='x+y+name'
            ))
        # Layout
        fig.update_layout(
            title=f'{symbol} Candlestick Chart',
            xaxis_title='Date',
            yaxis_title='',
            yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False, range=[0, chart_data_window['Volume'].max()*4]),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis_rangeslider_visible=False,
            height=700,
            dragmode='pan'
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "scrollZoom": True,
                "modeBarButtonsToAdd": ["drawline", "eraseshape"],
                "displayModeBar": True
            }
        )

        # --- RSI Pane (use full history, plot only visible period) ---
        def compute_rsi(series, period=14):
            delta = series.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi

        rsi_full = compute_rsi(full_data['Close'])
        rsi = rsi_full.loc[chart_data_window.index]
        rsi_fig = go.Figure()
        rsi_fig.add_trace(go.Scatter(
            x=chart_data_window.index,
            y=rsi,
            mode='lines',
            name='RSI',
            line=dict(color='purple', width=2)
        ))
        rsi_fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="Overbought", annotation_position="top right")
        rsi_fig.add_hline(y=40, line_dash="dash", line_color="green", annotation_text="Oversold", annotation_position="bottom right")
        rsi_fig.update_layout(
            title=f"{symbol} RSI (14)",
            xaxis_title='Date',
            yaxis_title='RSI',
            height=250,
            margin=dict(l=40, r=40, t=40, b=40)
        )
        st.plotly_chart(rsi_fig, use_container_width=True)
    else:
        st.warning("No chart data available for this stock.")
