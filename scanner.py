import pandas as pd
import pandas_ta as ta
import time
from stock_data import fetch_stock_chart_data

def scan_stocks_for_pattern(pattern_name, interval, start_date, end_date, cancel_event=None, progress_callback=None):
    print(f"[SCAN_START] Scanning for pattern: {pattern_name}")
    if progress_callback:
        progress_callback("[SCAN_START]")
    pattern_map = {
        "Hammer": "cdl_hammer",
        "Inverted Hammer": "cdl_inverted_hammer",
        "Bullish Engulfing": "cdl_engulfing",
        "Bearish Engulfing": "cdl_engulfing",
        "Morning Star": "cdl_morningstar",
        "Evening Star": "cdl_eveningstar",
        "Doji": "cdl_doji",
        "Shooting Star": "cdl_shootingstar",
        "Hanging Man": "cdl_hangingman",
        "Piercing Line": "cdl_piercing",
        "Dark Cloud Cover": "cdl_darkcloudcover",
        "3 White Soldiers": "cdl_3whitesoldiers",
        "3 Black Crows": "cdl_3blackcrows",
        "Sandwich": "cdl_sandwich"
    }
    is_bullish = pattern_name in ["Hammer", "Inverted Hammer", "Bullish Engulfing", "Morning Star", "Piercing Line", "3 White Soldiers", "Sandwich"]
    is_bearish = pattern_name in ["Bearish Engulfing", "Evening Star", "Shooting Star", "Hanging Man", "Dark Cloud Cover", "3 Black Crows"]
    pattern_func = pattern_map.get(pattern_name)
    if not pattern_func:
        return []
    stock_df = pd.read_csv("EQUITY_L.csv")
    symbols = stock_df['SYMBOL'].tolist()
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    matches = []
    for symbol in symbols:
        if cancel_event and cancel_event.is_set():
            break
        print(f"[SCANNING] {symbol}")
        if progress_callback:
            progress_callback(symbol)
        df = fetch_stock_chart_data(symbol, start_date=start_str, end_date=end_str, interval=interval)
        if df is not None and not df.empty and len(df) >= 10:
            df_ta = df.rename(columns={"Open": "open", "High": "high", "Low": "low", "Close": "close"})
            try:
                pattern_series = getattr(ta, pattern_func)(df_ta['open'], df_ta['high'], df_ta['low'], df_ta['close'])
                last10 = pattern_series[-10:]
                if pattern_name == "Bullish Engulfing":
                    found = (last10 == 100).any()
                elif pattern_name == "Bearish Engulfing":
                    found = (last10 == -100).any()
                else:
                    if is_bullish:
                        found = (last10 == 100).any()
                    elif is_bearish:
                        found = (last10 == -100).any()
                    else:
                        found = (last10 != 0).any()
                if found:
                    matches.append(symbol)
            except Exception:
                pass
        time.sleep(0.01)
    print(f"[SCAN_END] Scanning complete for pattern: {pattern_name}")
    if progress_callback:
        progress_callback("[SCAN_END]")
    return matches
