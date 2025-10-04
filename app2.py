"""
Refactored Trading Application with Modular Components
"""
import streamlit as st

# Import modular components
from ui.session_state import SessionStateManager
from ui.components.ema_controls import EMAControls
from ui.components.toolbar import Toolbar, TechnicalPanels
from ui.chart_renderer import PlotlyChartRenderer
from services.scanner_service import ScannerService, ScannerUI

# Set page configuration
st.set_page_config(layout="wide")

def main():
    """Main application entry point"""
    # Initialize session state
    SessionStateManager.init_all()

    # Initialize scanner service
    scanner_service = ScannerService()

    # Main title
    st.markdown("## Stock Chart Viewer")

    # Render toolbar and get parameters
    symbol, interval, start_date, end_date = Toolbar.render_advanced(
        on_change_callback=SessionStateManager.trigger_chart_refresh
    )

    # Render EMA controls
    EMAControls.render(on_change_callback=SessionStateManager.trigger_chart_refresh)

    # Render technical analysis panels
    show_bollinger = TechnicalPanels.render_bollinger_toggle(
        on_change_callback=SessionStateManager.trigger_chart_refresh
    )

    show_pivot_highs, show_pivot_lows = TechnicalPanels.render_pivot_toggles(
        on_change_callback=SessionStateManager.trigger_chart_refresh
    )

    TechnicalPanels.render_custom_strategy_panel()

    # Render main chart
    render_chart_section(symbol, interval, start_date, end_date,
                         show_bollinger, show_pivot_highs, show_pivot_lows)

    # Render scanner sidebars
    ScannerUI.render_candlestick_scanner(scanner_service, symbol, interval, start_date, end_date)
    ScannerUI.render_chart_pattern_scanner(scanner_service, symbol, interval, start_date, end_date)

def render_chart_section(symbol, interval, start_date, end_date,
                        show_bollinger, show_pivot_highs, show_pivot_lows):
    """Render the main chart section"""
    # Auto-refresh chart if needed
    if st.session_state.get('show_chart_auto2', False):
        st.session_state['show_chart_auto2'] = False
        render_chart = True
    else:
        render_chart = False

    # Manual chart refresh button
    if st.button("Show Chart", key="show_chart_btn"):
        render_chart = True

    if render_chart:
        ema_list = EMAControls.get_ema_list()
        PlotlyChartRenderer.render(
            symbol=symbol,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            show_bollinger=show_bollinger,
            show_pivot_highs=show_pivot_highs,
            show_pivot_lows=show_pivot_lows,
            ema_list=ema_list
        )

if __name__ == "__main__":
    main()