import streamlit as st
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor
from scanner import scan_stocks_for_pattern
from stock_data import get_all_stock_symbols, fetch_stock_chart_data
from chart_patterns import detect_double_top

class ScannerService:
    """Unified scanner service for both candlestick and chart patterns"""

    def __init__(self):
        self.executor = None

    def get_executor(self):
        """Get or create thread executor"""
        if self.executor is None:
            self.executor = ThreadPoolExecutor(max_workers=2)
        return self.executor

    def start_candlestick_scan(self, pattern_name, interval, start_date, end_date,
                              result_queue, cancel_event, progress_queue=None):
        """
        Start candlestick pattern scanning

        Args:
            pattern_name: Name of the candlestick pattern
            interval: Time interval for data
            start_date: Start date for scanning
            end_date: End date for scanning
            result_queue: Queue to put results
            cancel_event: Event to signal cancellation
            progress_queue: Queue for progress updates
        """
        def scanner_thread():
            def progress_callback(symbol):
                if progress_queue:
                    progress_queue.put(symbol)

            results = scan_stocks_for_pattern(
                pattern_name, interval, start_date, end_date,
                cancel_event, progress_callback
            )

            result_queue.put({
                'pattern': pattern_name,
                'results': results,
                'cancelled': cancel_event.is_set() if cancel_event else False
            })

        self.get_executor().submit(scanner_thread)

    def start_chart_pattern_scan(self, pattern_name, interval, start_date, end_date,
                                result_queue, cancel_event, progress_queue=None):
        """
        Start chart pattern scanning

        Args:
            pattern_name: Name of the chart pattern
            interval: Time interval for data
            start_date: Start date for scanning
            end_date: End date for scanning
            result_queue: Queue to put results
            cancel_event: Event to signal cancellation
            progress_queue: Queue for progress updates
        """
        def chart_pattern_scan_thread():
            results = []
            symbols = get_all_stock_symbols()

            for symbol in symbols:
                if cancel_event and cancel_event.is_set():
                    break

                if progress_queue:
                    progress_queue.put(symbol)

                try:
                    chart_data = fetch_stock_chart_data(
                        symbol, interval=interval,
                        start_date=start_date, end_date=end_date
                    )

                    if chart_data is None or chart_data.empty:
                        continue

                    # For now, only handle Double Top pattern
                    # This can be extended to support other patterns
                    if pattern_name == "Double Top":
                        double_tops = detect_double_top(chart_data)
                        if double_tops:
                            first_top_idx, pivot_low_idx, second_top_idx = double_tops[0]
                            dt_index = chart_data.index if hasattr(chart_data.index, 'to_list') else chart_data['Date']
                            result = {
                                "symbol": symbol,
                                "pattern": pattern_name,
                                "first_top_idx": first_top_idx,
                                "first_top_date": str(dt_index[first_top_idx]),
                                "pivot_low_idx": pivot_low_idx,
                                "pivot_low_date": str(dt_index[pivot_low_idx]),
                                "second_top_idx": second_top_idx,
                                "second_top_date": str(dt_index[second_top_idx]),
                            }
                            results.append(result)

                    time.sleep(0.01)  # Small delay to prevent overwhelming the system

                except Exception as e:
                    print(f"Error scanning {symbol}: {e}")
                    continue

            result_queue.put({
                'pattern': pattern_name,
                'results': results,
                'cancelled': cancel_event.is_set() if cancel_event else False
            })

        self.get_executor().submit(chart_pattern_scan_thread)

class ScannerUI:
    """UI components for scanner functionality"""

    CANDLESTICK_PATTERNS = [
        "Hammer", "Inverted Hammer", "Bullish Engulfing", "Bearish Engulfing",
        "Morning Star", "Evening Star", "Doji", "Shooting Star", "Hanging Man",
        "Piercing Line", "Dark Cloud Cover", "3 White Soldiers", "3 Black Crows", "Sandwich"
    ]

    CHART_PATTERNS = [
        "Double Top", "Double Bottom", "Head and Shoulders",
        "Inverted Head and Shoulders", "Flag and Pole", "Inverted Flag and Pole"
    ]

    @staticmethod
    def render_candlestick_scanner(scanner_service, symbol, interval, start_date, end_date):
        """Render candlestick pattern scanner UI"""
        st.sidebar.header("Candlestick Pattern Scanner")

        # Pattern selection
        selected_pattern = st.sidebar.selectbox(
            "Select Candlestick Pattern",
            ScannerUI.CANDLESTICK_PATTERNS,
            key="pattern_select"
        )

        # Scanner status
        scan_running = st.session_state.get('scanner_status') == 'running'

        # Scan button
        if st.sidebar.button("Scan for Pattern", disabled=scan_running, key="scan_btn"):
            ScannerUI._start_candlestick_scan(scanner_service, selected_pattern, interval, start_date, end_date)

        # Cancel button
        if st.sidebar.button("Cancel Scan", disabled=not scan_running, key="cancel_btn"):
            ScannerUI._cancel_scan('scanner')

        # Process results
        ScannerUI._process_scanner_results()

        # Show progress
        ScannerUI._show_scan_progress('scanner')

        # Show results
        ScannerUI._show_scan_results('scanner')

    @staticmethod
    def render_chart_pattern_scanner(scanner_service, symbol, interval, start_date, end_date):
        """Render chart pattern scanner UI"""
        st.sidebar.header("Chart Pattern Scanner")

        # Pattern selection
        selected_chart_pattern = st.sidebar.selectbox(
            "Select Chart Pattern",
            ScannerUI.CHART_PATTERNS,
            key="chart_pattern_select"
        )

        # Scanner status
        chart_scan_running = st.session_state.get('chart_scanner_status') == 'running'

        # Scan button
        if st.sidebar.button("Scan for Chart Pattern", disabled=chart_scan_running, key="scan_chart_pattern_btn"):
            ScannerUI._start_chart_pattern_scan(scanner_service, selected_chart_pattern, interval, start_date, end_date)

        # Cancel button
        if st.sidebar.button("Cancel Chart Pattern Scan", disabled=not chart_scan_running, key="cancel_chart_pattern_btn"):
            ScannerUI._cancel_scan('chart_scanner')

        # Process results
        ScannerUI._process_chart_scanner_results()

        # Show progress
        ScannerUI._show_scan_progress('chart_scanner')

        # Show chart pattern results
        ScannerUI._show_chart_pattern_results(selected_chart_pattern)

    @staticmethod
    def _start_candlestick_scan(scanner_service, pattern_name, interval, start_date, end_date):
        """Start candlestick pattern scan"""
        st.session_state['scanner_status'] = 'running'
        st.session_state['scanner_results'] = []
        st.session_state['scanner_pattern'] = pattern_name
        st.session_state['scanner_toast'] = False
        st.session_state['scanner_cancel_event'].clear()

        scanner_service.start_candlestick_scan(
            pattern_name, interval, start_date, end_date,
            st.session_state['scanner_queue'],
            st.session_state['scanner_cancel_event'],
            st.session_state['scanner_progress_queue']
        )

    @staticmethod
    def _start_chart_pattern_scan(scanner_service, pattern_name, interval, start_date, end_date):
        """Start chart pattern scan"""
        st.session_state['chart_scanner_status'] = 'running'
        st.session_state['chart_scanner_results'] = []
        st.session_state['chart_scanner_cancel_event'].clear()

        scanner_service.start_chart_pattern_scan(
            pattern_name, interval, start_date, end_date,
            st.session_state['chart_scanner_queue'],
            st.session_state['chart_scanner_cancel_event'],
            st.session_state['chart_scanner_progress_queue']
        )

    @staticmethod
    def _cancel_scan(scanner_type):
        """Cancel running scan"""
        if scanner_type == 'scanner':
            st.session_state['scanner_cancel_event'].set()
            st.session_state['scanner_status'] = 'idle'
        elif scanner_type == 'chart_scanner':
            st.session_state['chart_scanner_cancel_event'].set()
            st.session_state['chart_scanner_status'] = 'idle'

    @staticmethod
    def _process_scanner_results():
        """Process candlestick scanner results"""
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
        except Exception:
            pass

    @staticmethod
    def _process_chart_scanner_results():
        """Process chart pattern scanner results"""
        try:
            chart_scanner_queue = st.session_state.get('chart_scanner_queue')
            if chart_scanner_queue:
                while not chart_scanner_queue.empty():
                    result = chart_scanner_queue.get_nowait()
                    st.session_state['chart_scanner_results'] = result['results']
                    if result['cancelled']:
                        st.session_state['chart_scanner_status'] = 'idle'
                    else:
                        st.session_state['chart_scanner_status'] = 'done'
        except Exception:
            pass

    @staticmethod
    def _show_scan_progress(scanner_type):
        """Show scanning progress"""
        status_key = f'{scanner_type}_status'
        progress_key = f'{scanner_type}_progress_queue'

        if st.session_state.get(status_key) == 'running':
            progress_placeholder = st.sidebar.empty()
            last_scanned = None

            # Check for progress updates
            try:
                progress_queue = st.session_state.get(progress_key)
                if progress_queue:
                    while not progress_queue.empty():
                        last_scanned = progress_queue.get_nowait()
            except Exception:
                pass

            if last_scanned:
                progress_placeholder.info(f"Scanning: {last_scanned}")

    @staticmethod
    def _show_scan_results(scanner_type):
        """Show candlestick scan results"""
        # Toast alert when scan is done
        if st.session_state.get('scanner_toast', False):
            results_count = len(st.session_state.get('scanner_results', []))
            st.sidebar.success(f"Scan done: {results_count} results found.")
            st.session_state['scanner_toast'] = False

        # Show status
        if st.session_state.get('scanner_status') == 'running':
            st.sidebar.info("Scanning all stocks for pattern")

    @staticmethod
    def _show_chart_pattern_results(selected_pattern):
        """Show chart pattern scan results"""
        if st.session_state.get('chart_scanner_status') == 'running':
            st.sidebar.info(f"Scanning for {selected_pattern}...")

        if st.session_state.get('chart_scanner_status') == 'done':
            results = st.session_state.get('chart_scanner_results', [])
            if results:
                st.sidebar.success(f"Found {len(results)} stocks with {selected_pattern}")
                for r in results:
                    if 'first_top_date' in r:  # Double top format
                        st.sidebar.write(f"{r['symbol']}: Top1 {r['first_top_date']}, Pivot {r['pivot_low_date']}, Top2 {r['second_top_date']}")
            else:
                st.sidebar.info(f"No {selected_pattern} found in any stock.")