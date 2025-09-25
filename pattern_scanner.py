import pandas as pd
from chart_patterns import detect_double_top
from stock_data import get_all_stock_symbols, fetch_stock_chart_data

def scan_stocks_for_double_top(interval="1d", start_date=None, end_date=None, cancel_event=None):
    results = []
    symbols = get_all_stock_symbols()
    for symbol in symbols:
        if cancel_event and cancel_event.is_set():
            break
        try:
            chart_data = fetch_stock_chart_data(symbol, interval=interval, start_date=start_date, end_date=end_date)
            if chart_data is None or chart_data.empty:
                continue
            dt_index = chart_data.index if hasattr(chart_data.index, 'to_list') else chart_data['Date']
            double_tops = detect_double_top(chart_data)
            if double_tops:
                # Only report the first double top found
                first_top_idx, pivot_low_idx, second_top_idx = double_tops[0]
                result = {
                    "symbol": symbol,
                    "first_top_idx": first_top_idx,
                    "first_top_date": str(dt_index[first_top_idx]),
                    "pivot_low_idx": pivot_low_idx,
                    "pivot_low_date": str(dt_index[pivot_low_idx]),
                    "second_top_idx": second_top_idx,
                    "second_top_date": str(dt_index[second_top_idx]),
                }
                results.append(result)
        except Exception as e:
            print(f"Error scanning {symbol}: {e}")
    return results

# Example usage:
# results = scan_stocks_for_double_top()
# for r in results:
#     print(r)
