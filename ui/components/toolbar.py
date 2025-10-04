import streamlit as st
import pandas as pd
from ui.session_state import get_default_dates, DEFAULT_SYMBOL

class Toolbar:
    """UI component for date range and symbol selection toolbar"""

    @staticmethod
    def render_advanced(on_change_callback=None):
        """
        Render advanced toolbar with stock selection dropdown (for app2.py)

        Args:
            on_change_callback: Function to call when settings change

        Returns:
            tuple: (symbol, interval, start_date, end_date)
        """
        st.markdown(
            "<div style='background-color:#f0f2f6;padding:10px 0 10px 0;margin-bottom:10px;'>"
            "<h2 style='display:inline;margin-right:30px;'>NSE Stock Candlestick Viewer (Plotly)</h2>",
            unsafe_allow_html=True
        )

        toolbar1_col1, toolbar1_col2 = st.columns([3, 1])

        with toolbar1_col1:
            # Load stock data
            try:
                stock_df = pd.read_csv("EQUITY_L.csv")
                stock_options = [f"{row['SYMBOL']} - {row['NAME OF COMPANY']}" for _, row in stock_df.iterrows()]

                # Find current selection index
                current_symbol = st.session_state.get('selected_symbol', DEFAULT_SYMBOL)
                default_index = 0
                try:
                    current_option = f"{current_symbol} - " + stock_df.loc[stock_df['SYMBOL'] == current_symbol, 'NAME OF COMPANY'].values[0]
                    default_index = stock_options.index(current_option)
                except (IndexError, ValueError):
                    pass

                selected_stock = st.selectbox(
                    "Chart Name (Symbol)",
                    options=stock_options,
                    index=default_index,
                    key="chart_name_select2"
                )
                symbol = selected_stock.split(" - ")[0]
                st.session_state['selected_symbol'] = symbol

            except Exception as e:
                st.error(f"Error loading stock list: {e}")
                symbol = st.text_input("Symbol", value=DEFAULT_SYMBOL, key="manual_symbol_input")
                st.session_state['selected_symbol'] = symbol

        with toolbar1_col2:
            def on_interval_change():
                if on_change_callback:
                    on_change_callback()
                st.session_state['interval'] = st.session_state['interval_select2']

            interval = st.selectbox(
                "Interval",
                ["1d", "1wk", "1mo"],
                index=["1d", "1wk", "1mo"].index(st.session_state.get('interval', '1d')),
                key="interval_select2",
                on_change=on_interval_change
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Date range selection
        st.markdown(
            "<div style='background-color:#f0f2f6;padding:10px 0 10px 0;margin-top:10px;'>"
            "<b>Select Date Range</b>",
            unsafe_allow_html=True
        )

        default_start, default_end = get_default_dates()
        toolbar2_col1, toolbar2_col2 = st.columns(2)

        with toolbar2_col1:
            start_date = st.date_input("Start Date", default_start, key="start_date2")
        with toolbar2_col2:
            end_date = st.date_input("End Date", default_end, key="end_date2")

        st.markdown("</div>", unsafe_allow_html=True)

        return symbol, interval, start_date, end_date

    @staticmethod
    def render_simple():
        """
        Render simple toolbar with text input (for app.py)

        Returns:
            tuple: (symbol, interval, start_date, end_date)
        """
        st.markdown(
            "<div style='background-color:#f0f2f6;padding:10px 0 10px 0;margin-bottom:10px;'>"
            "<h2 style='display:inline;margin-right:30px;'>NSE Stock Candlestick Viewer</h2>",
            unsafe_allow_html=True
        )

        toolbar1_col1, toolbar1_col2 = st.columns([3, 1])

        # Callback functions
        def update_chart_name_from_watchlist():
            st.session_state['chart_name_input'] = st.session_state['selected_symbol']

        def refresh_chart_on_interval():
            st.session_state['interval'] = st.session_state['interval_select']
            st.session_state['show_chart_auto'] = True

        with toolbar1_col1:
            chart_name = st.text_input(
                "Chart Name (Symbol)",
                value=st.session_state.get('selected_symbol', DEFAULT_SYMBOL),
                key="chart_name_input"
            )

        with toolbar1_col2:
            interval = st.selectbox(
                "Interval",
                ["1d", "1wk", "1mo"],
                index=["1d", "1wk", "1mo"].index(st.session_state.get('interval', '1d')),
                key="interval_select",
                on_change=refresh_chart_on_interval
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Date range selection
        st.markdown(
            "<div style='background-color:#f0f2f6;padding:10px 0 10px 0;margin-top:10px;'>"
            "<b>Select Date Range</b>",
            unsafe_allow_html=True
        )

        default_start, default_end = get_default_dates()
        toolbar2_col1, toolbar2_col2 = st.columns(2)

        with toolbar2_col1:
            start_date = st.date_input("Start Date", default_start, key="start_date")
        with toolbar2_col2:
            end_date = st.date_input("End Date", default_end, key="end_date")

        st.markdown("</div>", unsafe_allow_html=True)

        return chart_name, interval, start_date, end_date

class TechnicalPanels:
    """UI components for technical analysis panels"""

    @staticmethod
    def render_bollinger_toggle(on_change_callback=None):
        """Render Bollinger Bands toggle"""
        return st.checkbox(
            "Show Bollinger Bands",
            value=False,
            key="show_bollinger",
            on_change=on_change_callback
        )

    @staticmethod
    def render_pivot_toggles(on_change_callback=None):
        """Render pivot high/low toggles"""
        st.markdown(
            "<div style='background-color:#e3e6ea;padding:10px 0 10px 0;margin-bottom:10px;'>"
            "<b>Technical Analysis: Pivots</b>",
            unsafe_allow_html=True
        )

        pivot_col1, pivot_col2 = st.columns(2)
        with pivot_col1:
            show_pivot_highs = st.checkbox(
                "Show Pivot Highs",
                value=False,
                key="show_pivot_highs",
                on_change=on_change_callback
            )
        with pivot_col2:
            show_pivot_lows = st.checkbox(
                "Show Pivot Lows",
                value=False,
                key="show_pivot_lows",
                on_change=on_change_callback
            )

        st.markdown("</div>", unsafe_allow_html=True)
        return show_pivot_highs, show_pivot_lows

    @staticmethod
    def render_custom_strategy_panel():
        """Render custom strategy input panel"""
        st.markdown(
            "<div style='background-color:#e3e6ea;padding:10px 0 10px 0;margin-bottom:10px;'>"
            "<b>Technical Analysis: Custom Strategy</b>",
            unsafe_allow_html=True
        )

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

class WatchlistPanel:
    """UI component for watchlist management (app.py)"""

    @staticmethod
    def render():
        """Render watchlist panel"""
        st.header("Watchlist")

        # Ensure watchlist exists
        if 'watchlist' not in st.session_state:
            st.session_state['watchlist'] = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]

        # Add to watchlist
        new_watch = st.text_input("Add to Watchlist", "")

        def add_to_watchlist():
            if new_watch and new_watch not in st.session_state['watchlist']:
                st.session_state['watchlist'].append(new_watch.upper())

        st.button("Add", key="add_watch", on_click=add_to_watchlist)

        # Remove from watchlist
        remove_watch = st.selectbox("Remove from Watchlist", st.session_state['watchlist'], key="remove_watch")

        def remove_from_watchlist():
            if remove_watch in st.session_state['watchlist']:
                st.session_state['watchlist'].remove(remove_watch)

        st.button("Remove", key="remove_btn", on_click=remove_from_watchlist)

        # Select from watchlist
        def update_chart_name_from_watchlist():
            st.session_state['chart_name_input'] = st.session_state['selected_symbol']

        selected_watch = st.radio(
            "Select Stock",
            st.session_state['watchlist'],
            index=st.session_state['watchlist'].index(st.session_state.get('selected_symbol', DEFAULT_SYMBOL))
                  if st.session_state.get('selected_symbol', DEFAULT_SYMBOL) in st.session_state['watchlist'] else 0,
            key="watchlist_radio",
            on_change=update_chart_name_from_watchlist
        )

        # Update selected symbol if watchlist selection changes
        if selected_watch != st.session_state.get('selected_symbol'):
            st.session_state['selected_symbol'] = selected_watch

        return selected_watch