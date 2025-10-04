"""
Trading Application with MPLFinance Charts (Refactored)
"""
import streamlit as st
import pandas as pd

# Import modular components
from ui.session_state import SessionStateManager
from ui.components.ema_controls import EMAControls
from ui.components.toolbar import Toolbar, WatchlistPanel
from ui.chart_renderer import MPLFinanceChartRenderer
from stock_data import fetch_stock_chart_data

# Set page configuration
st.set_page_config(layout="wide")

def main():
    """Main application entry point"""
    # Initialize session state
    SessionStateManager.init_all()

    # Render EMA controls (placed at top as in original)
    EMAControls.render_simple()

    # Render toolbar
    chart_name, interval, start_date, end_date = Toolbar.render_simple()

    # Main layout: Chart center, Watchlist right
    main_col, watch_col = st.columns([7, 2])

    with watch_col:
        WatchlistPanel.render()

    # Chart display logic
    if 'show_chart_auto' not in st.session_state:
        st.session_state['show_chart_auto'] = False

    with main_col:
        st.subheader(f"Candlestick Chart: {st.session_state.get('selected_symbol', 'RELIANCE')}")
        show_chart = st.button("Show Chart", key="show_chart_btn")

        # Auto-refresh chart if interval changed
        if st.session_state.get('show_chart_auto', False):
            show_chart = True
            st.session_state['show_chart_auto'] = False

        if show_chart:
            # Use chart_name input as the selected symbol
            symbol = st.session_state.get('chart_name_input', 'RELIANCE').upper()
            st.session_state['selected_symbol'] = symbol
            st.session_state['interval'] = st.session_state.get('interval_select', '1d')

            chart_data = fetch_stock_chart_data(
                symbol,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                interval=st.session_state['interval']
            )

            if not chart_data.empty:
                ema_list = EMAControls.get_ema_list()
                MPLFinanceChartRenderer.render(chart_data, symbol, ema_list)
            else:
                st.warning("No chart data available for this stock.")

if __name__ == "__main__":
    main()