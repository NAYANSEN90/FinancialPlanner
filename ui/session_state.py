import streamlit as st
import pandas as pd
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

# Default values
DEFAULT_SYMBOL = "RELIANCE"
DEFAULT_INTERVAL = "1d"

def get_default_dates():
    """Get default start and end dates"""
    today = pd.Timestamp.today().normalize()
    return today - pd.DateOffset(years=1), today

class SessionStateManager:
    """Centralized session state management for the trading application"""

    @staticmethod
    def init_chart_state():
        """Initialize chart-related session state"""
        default_start, default_end = get_default_dates()

        if 'ema_list' not in st.session_state:
            st.session_state['ema_list'] = [{'period': 20, 'visible': True}]
        if 'selected_symbol' not in st.session_state:
            st.session_state['selected_symbol'] = DEFAULT_SYMBOL
        if 'interval' not in st.session_state:
            st.session_state['interval'] = DEFAULT_INTERVAL
        if 'show_chart_auto2' not in st.session_state:
            st.session_state['show_chart_auto2'] = False
        if 'window_start_idx' not in st.session_state:
            st.session_state['window_start_idx'] = 0
        if 'show_dow_theory' not in st.session_state:
            st.session_state['show_dow_theory'] = False

    @staticmethod
    def init_scanner_state():
        """Initialize scanner-related session state"""
        # Candlestick pattern scanner
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
        if 'scanner_progress_queue' not in st.session_state:
            st.session_state['scanner_progress_queue'] = queue.Queue()

        # Chart pattern scanner
        if 'chart_scanner_status' not in st.session_state:
            st.session_state['chart_scanner_status'] = 'idle'
        if 'chart_scanner_cancel_event' not in st.session_state:
            st.session_state['chart_scanner_cancel_event'] = threading.Event()
        if 'chart_scanner_results' not in st.session_state:
            st.session_state['chart_scanner_results'] = []
        if 'chart_scanner_queue' not in st.session_state:
            st.session_state['chart_scanner_queue'] = queue.Queue()
        if 'chart_scanner_progress_queue' not in st.session_state:
            st.session_state['chart_scanner_progress_queue'] = queue.Queue()

        # Thread executor
        if 'scanner_executor' not in st.session_state:
            st.session_state['scanner_executor'] = ThreadPoolExecutor(max_workers=2)

    @staticmethod
    def init_watchlist_state():
        """Initialize watchlist-related session state for app.py"""
        if 'watchlist' not in st.session_state:
            st.session_state['watchlist'] = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]
        if 'show_chart_auto' not in st.session_state:
            st.session_state['show_chart_auto'] = False

    @staticmethod
    def init_all():
        """Initialize all session state"""
        SessionStateManager.init_chart_state()
        SessionStateManager.init_scanner_state()
        SessionStateManager.init_watchlist_state()

    @staticmethod
    def trigger_chart_refresh():
        """Trigger chart refresh"""
        st.session_state['show_chart_auto2'] = True

    @staticmethod
    def is_scanner_running():
        """Check if any scanner is currently running"""
        return (st.session_state.get('scanner_status') == 'running' or
                st.session_state.get('chart_scanner_status') == 'running')

    @staticmethod
    def get_scanner_results():
        """Get current scanner results"""
        return {
            'candlestick': {
                'pattern': st.session_state.get('scanner_pattern'),
                'results': st.session_state.get('scanner_results', [])
            },
            'chart': {
                'results': st.session_state.get('chart_scanner_results', [])
            }
        }