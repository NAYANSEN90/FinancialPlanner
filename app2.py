
from concurrent.futures import ThreadPoolExecutor
from scanner import scan_stocks_for_pattern
import streamlit as st
import threading
import queue

def scanner_thread(pattern_name, interval, start_date, end_date, result_queue, cancel_event, progress_queue=None):
    def progress_callback(symbol):
        if progress_queue:
            progress_queue.put(symbol)
    results = scan_stocks_for_pattern(pattern_name, interval, start_date, end_date, cancel_event, progress_callback)
    result_queue.put({
        'pattern': pattern_name,
        'results': results,
        'cancelled': cancel_event.is_set() if cancel_event else False
    })

# --- Bollinger Bands Toggle (place after Streamlit setup, before chart rendering) ---
def on_bollinger_toggle():
    st.session_state['show_chart_auto2'] = True

# ...existing code...

# Place this just before chart rendering logic:
# show_bollinger = st.checkbox("Show Bollinger Bands", value=False, key="show_bollinger", on_change=on_bollinger_toggle)

# --- Technical Analysis Panel: Custom Strategy Input ---
def show_custom_strategy_panel():
    st.markdown("<div style='background-color:#e3e6ea;padding:10px 0 10px 0;margin-bottom:10px;'><b>Technical Analysis: Custom Strategy</b>", unsafe_allow_html=True)
    custom_strategy = st.text_area(
        "Describe your strategy in English (e.g. 'Show a buy signal when the 20 EMA crosses above the 50 EMA and RSI is below 40'):",
        value="",
        key="custom_strategy_input"
    )
    analyze_btn = st.button("Analyze Strategy", key="analyze_strategy_btn")
    if analyze_btn and custom_strategy.strip():
        st.info(f"Strategy submitted: {custom_strategy}")
        st.warning("Strategy parsing and execution is not yet implemented. This is a placeholder for future AI-powered analysis.")
    st.markdown("</div>", unsafe_allow_html=True)


# ...existing code...

# Call the panel after Streamlit is imported and initialized
# (Move this call to just after Streamlit initialization and before the rest of the UI)

import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from stock_data import fetch_stock_chart_data

st.set_page_config(layout="wide")

# ========== Defaults & Session State ========== #
today = pd.Timestamp.today().normalize()
default_end = today
default_start = today - pd.DateOffset(years=1)
default_symbol = "RELIANCE"
default_interval = "1d"

def init_session_state():
    if 'ema_list' not in st.session_state:
        st.session_state['ema_list'] = [{'period': 20, 'visible': True}]
    if 'selected_symbol' not in st.session_state:
        st.session_state['selected_symbol'] = default_symbol
    if 'interval' not in st.session_state:
        st.session_state['interval'] = default_interval
    if 'show_chart_auto2' not in st.session_state:
        st.session_state['show_chart_auto2'] = False
    if 'window_start_idx' not in st.session_state:
        st.session_state['window_start_idx'] = 0

init_session_state()

# ========== Helper Functions ========== #
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

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# ========== UI Sections ========== #
def ema_controls():
    def on_ema_change():
        st.session_state['show_chart_auto2'] = True
    def add_ema_callback():
        st.session_state['ema_list'].append({'period': 20, 'visible': True})
        st.session_state['show_chart_auto2'] = True
    def remove_ema_callback():
        if len(st.session_state['ema_list']) > 1:
            st.session_state['ema_list'].pop()
            st.session_state['show_chart_auto2'] = True
    st.markdown("<div style='background-color:#e3e6ea;padding:10px 0 10px 0;margin-bottom:10px;'><b>Indicators: Exponential Moving Average (EMA)</b>", unsafe_allow_html=True)
    ema_cols = st.columns([2,2,2,2,2])
    for i, ema in enumerate(st.session_state['ema_list']):
        unique_key = f"{i}_{id(ema)}"
        with ema_cols[i % 5]:
            st.session_state['ema_list'][i]['period'] = st.number_input(
                f"EMA {i+1} Period", min_value=1, max_value=200, value=ema['period'], key=f"ema_period_{unique_key}", on_change=on_ema_change)
            st.session_state['ema_list'][i]['visible'] = st.checkbox(
                f"Show EMA {i+1}", value=ema['visible'], key=f"ema_visible_{unique_key}", on_change=on_ema_change)
    st.button("Add EMA", key="add_ema_btn", on_click=add_ema_callback)
    st.button("Remove Last EMA", key="remove_ema_btn", on_click=remove_ema_callback)
    st.markdown("</div>", unsafe_allow_html=True)

def toolbar_and_date():
    st.markdown("<div style='background-color:#f0f2f6;padding:10px 0 10px 0;margin-bottom:10px;'><h2 style='display:inline;margin-right:30px;'>NSE Stock Candlestick Viewer (Plotly)</h2>", unsafe_allow_html=True)
    toolbar1_col1, toolbar1_col2 = st.columns([3,1])
    with toolbar1_col1:
        stock_df = pd.read_csv("EQUITY_L.csv")
        stock_options = [f"{row['SYMBOL']} - {row['NAME OF COMPANY']}" for _, row in stock_df.iterrows()]
        selected_stock = st.selectbox(
            "Chart Name (Symbol)",
            options=stock_options,
            index=stock_options.index(f"{st.session_state['selected_symbol']} - " + stock_df.loc[stock_df['SYMBOL'] == st.session_state['selected_symbol'], 'NAME OF COMPANY'].values[0]) if st.session_state['selected_symbol'] in stock_df['SYMBOL'].values else 0,
            key="chart_name_select2"
        )
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
    st.markdown("<div style='background-color:#f0f2f6;padding:10px 0 10px 0;margin-top:10px;'><b>Select Date Range</b>", unsafe_allow_html=True)
    toolbar2_col1, toolbar2_col2 = st.columns(2)
    with toolbar2_col1:
        start_date = st.date_input("Start Date", default_start, key="start_date2")
    with toolbar2_col2:
        end_date = st.date_input("End Date", default_end, key="end_date2")
    st.markdown("</div>", unsafe_allow_html=True)
    return symbol, interval, start_date, end_date

def bollinger_toggle():
    def on_bollinger_toggle():
        st.session_state['show_chart_auto2'] = True
    return st.checkbox("Show Bollinger Bands", value=False, key="show_bollinger", on_change=on_bollinger_toggle)

def pivot_toggles():
    def on_pivot_toggle():
        st.session_state['show_chart_auto2'] = True
    st.markdown("<div style='background-color:#e3e6ea;padding:10px 0 10px 0;margin-bottom:10px;'><b>Technical Analysis: Pivots</b>", unsafe_allow_html=True)
    pivot_col1, pivot_col2 = st.columns(2)
    with pivot_col1:
        show_pivot_highs = st.checkbox("Show Pivot Highs", value=False, key="show_pivot_highs", on_change=on_pivot_toggle)
    with pivot_col2:
        show_pivot_lows = st.checkbox("Show Pivot Lows", value=False, key="show_pivot_lows", on_change=on_pivot_toggle)
    st.markdown("</div>", unsafe_allow_html=True)
    return show_pivot_highs, show_pivot_lows

def show_custom_strategy_panel():
    st.markdown("<div style='background-color:#e3e6ea;padding:10px 0 10px 0;margin-bottom:10px;'><b>Technical Analysis: Custom Strategy</b>", unsafe_allow_html=True)
    custom_strategy = st.text_area(
        "Describe your strategy in English (e.g. 'Show a buy signal when the 20 EMA crosses above the 50 EMA and RSI is below 40'):",
        value="",
        key="custom_strategy_input"
    )
    analyze_btn = st.button("Analyze Strategy", key="analyze_strategy_btn")
    if analyze_btn and custom_strategy.strip():
        st.info(f"Strategy submitted: {custom_strategy}")
        st.warning("Strategy parsing and execution is not yet implemented. This is a placeholder for future AI-powered analysis.")
    st.markdown("</div>", unsafe_allow_html=True)

def render_charts(symbol, interval, start_date, end_date, show_bollinger, show_pivot_highs, show_pivot_lows):
    from stock_data import _stock_data_cache
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    chart_data = fetch_stock_chart_data(symbol, start_date=start_str, end_date=end_str, interval=interval)
    cache_key = f"{symbol}_{interval}"
    full_data = _stock_data_cache.get(cache_key, chart_data)
    MAX_CANDLES = 20000
    if len(chart_data) > MAX_CANDLES:
        window_start = st.session_state['window_start_idx']
        window_end = window_start + MAX_CANDLES
        if window_end > len(chart_data):
            window_end = len(chart_data)
            window_start = window_end - MAX_CANDLES
        nav_col1, _, nav_col3 = st.columns([1,2,1])
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
    if chart_data_window.empty:
        st.warning("No chart data available for this stock.")
        return
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=chart_data_window.index,
        open=chart_data_window['Open'],
        high=chart_data_window['High'],
        low=chart_data_window['Low'],
        close=chart_data_window['Close'],
        name='Candlestick'))
    fig.add_trace(go.Bar(
        x=chart_data_window.index,
        y=chart_data_window['Volume'],
        name='Volume',
        marker_color='rgba(50,50,150,0.7)',
        yaxis='y2',
        opacity=0.4
    ))
    vol_ma20 = full_data['Volume'].rolling(window=20).mean().loc[chart_data_window.index]
    fig.add_trace(go.Scatter(
        x=chart_data_window.index,
        y=vol_ma20,
        mode='lines',
        name='Volume MA 20',
        yaxis='y2',
        line=dict(color='orange', width=2, dash='dash')
    ))
    if show_bollinger:
        close_full = full_data['Close']
        bb_ma = close_full.rolling(window=20).mean().loc[chart_data_window.index]
        bb_std = close_full.rolling(window=20).std().loc[chart_data_window.index]
        upper_band = bb_ma + 2 * bb_std
        lower_band = bb_ma - 2 * bb_std
        fig.add_trace(go.Scatter(
            x=chart_data_window.index,
            y=upper_band,
            mode='lines',
            name='BB Upper',
            line=dict(color='blue', width=1, dash='dot'),
            opacity=0.7
        ))
        fig.add_trace(go.Scatter(
            x=chart_data_window.index,
            y=lower_band,
            mode='lines',
            name='BB Lower',
            line=dict(color='blue', width=1, dash='dot'),
            opacity=0.7
        ))
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
    fig.update_layout(
        title=f'{symbol} Candlestick Chart',
        xaxis_title='Date',
        yaxis_title='',
        yaxis2=dict(title='Volume', overlaying='y', side='right', showgrid=False, range=[0, chart_data_window['Volume'].max()*4]),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        xaxis_rangeslider_visible=False,
        height=700,
        dragmode='pan',
        hovermode='x',
        xaxis=dict(
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            showline=True,
            spikedash='dot',
            spikethickness=1,
            spikecolor='black',
        ),
        yaxis=dict(
            showspikes=True,
            spikemode='across',
            spikesnap='cursor',
            showline=True,
            spikedash='dot',
            spikethickness=1,
            spikecolor='black',
        )
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



# ========== MAIN APP ENTRYPOINT ========== #
def main():
    # --- Main Chart and Controls UI ---
    st.markdown("## Stock Chart Viewer")
    symbol, interval, start_date, end_date = toolbar_and_date()
    ema_controls()
    show_bollinger = bollinger_toggle()
    show_pivot_highs, show_pivot_lows = pivot_toggles()
    show_custom_strategy_panel()
    render_charts(symbol, interval, start_date, end_date, show_bollinger, show_pivot_highs, show_pivot_lows)
    # --- Ensure scanner session state keys are initialized ---
    if 'scanner_status' not in st.session_state:
        st.session_state['scanner_status'] = 'idle'  # idle, running, done
    if 'scanner_results' not in st.session_state:
        st.session_state['scanner_results'] = []
    if 'scanner_pattern' not in st.session_state:
        st.session_state['scanner_pattern'] = None
    if 'scanner_toast' not in st.session_state:
        st.session_state['scanner_toast'] = False
    if 'show_results_drawer' not in st.session_state:
        st.session_state['show_results_drawer'] = False
    if 'scanner_cancel' not in st.session_state:
        st.session_state['scanner_cancel'] = False
    if 'scanner_cancel_event' not in st.session_state:
        st.session_state['scanner_cancel_event'] = threading.Event()
    if 'scanner_queue' not in st.session_state:
        st.session_state['scanner_queue'] = queue.Queue()
    scan_running = st.session_state['scanner_status'] == 'running'
    scan_btn = st.sidebar.button("Scan for Pattern", key="scan_btn", disabled=scan_running)
    cancel_btn = st.sidebar.button("Cancel Scan", key="cancel_btn", disabled=not scan_running)

    # --- Drawer/Sidebar: Candlestick Pattern Selector ---
    st.sidebar.header("Candlestick Pattern Scanner")
    candlestick_patterns = [
        "Hammer", "Inverted Hammer", "Bullish Engulfing", "Bearish Engulfing", "Morning Star", "Evening Star",
        "Doji", "Shooting Star", "Hanging Man", "Piercing Line", "Dark Cloud Cover",
        "3 White Soldiers", "3 Black Crows", "Sandwich"
    ]
    selected_pattern = st.sidebar.selectbox("Select Candlestick Pattern", candlestick_patterns, key="pattern_select")

    # Check for results from the scanner thread
    try:
        while not st.session_state['scanner_queue'].empty():
            result = st.session_state['scanner_queue'].get_nowait()
            st.session_state['scanner_results'] = result['results']
            st.session_state['scanner_pattern'] = result['pattern']
            if result['cancelled']:
                st.session_state['scanner_status'] = 'idle'
            else:
                st.session_state['scanner_status'] = 'done'
                st.session_state['scanner_toast'] = True
            st.session_state['scanner_cancel'] = False
    except Exception:
        pass

    if scan_btn and selected_pattern:
        if st.session_state['scanner_status'] != 'running':
            st.session_state['scanner_status'] = 'running'
            st.session_state['scanner_results'] = []
            st.session_state['scanner_pattern'] = selected_pattern
            st.session_state['scanner_toast'] = False
            st.session_state['show_results_drawer'] = True
            st.session_state['scanner_cancel'] = False
            st.session_state['scanner_cancel_event'].clear()
            # Use ThreadPoolExecutor to manage threads efficiently
            executor = getattr(st.session_state, 'scanner_executor', None)
            if executor is None:
                executor = ThreadPoolExecutor(max_workers=2)
                st.session_state['scanner_executor'] = executor
            # Create a progress queue for UI updates
            if 'scanner_progress_queue' not in st.session_state:
                st.session_state['scanner_progress_queue'] = queue.Queue()
            executor.submit(
                scanner_thread,
                selected_pattern, interval, start_date, end_date,
                st.session_state['scanner_queue'],
                st.session_state['scanner_cancel_event'],
                st.session_state['scanner_progress_queue']
            )

    # Cancel scan logic: set the cancel event to stop the scanner thread
    if cancel_btn and st.session_state['scanner_status'] == 'running':
        st.session_state['scanner_cancel'] = True
        st.session_state['scanner_cancel_event'].set()
    # Show scanning progress in UI
    current_scanning = None
    try:
        while not st.session_state.get('scanner_progress_queue', queue.Queue()).empty():
            current_scanning = st.session_state['scanner_progress_queue'].get_nowait()
    except Exception:
        pass
    if st.session_state['scanner_status'] == 'running' and current_scanning:
        st.sidebar.info(f"Scanning: {current_scanning}")
    if cancel_btn and st.session_state['scanner_status'] == 'running':
        st.session_state['scanner_cancel'] = True
        st.session_state['scanner_cancel_event'].set()

    # Toast alert when scan is done
    if st.session_state.get('scanner_toast', False):
        st.sidebar.success(f"Scan done: {len(st.session_state['scanner_results'])} results found.")
        st.session_state['scanner_toast'] = False

    # Show status and results in drawer
    if st.session_state['scanner_status'] == 'running':
        st.sidebar.info("Scanning all stocks for pattern... (non-blocking)")

main()