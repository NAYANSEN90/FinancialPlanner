import pandas as pd
from typing import List, Dict, Any

def determine_dow_theory_regions(df: pd.DataFrame, pivot_high_indices, pivot_low_indices) -> List[Dict[str, Any]]:
    """
    Given a DataFrame with OHLC data and lists of pivot high/low indices (index labels),
    returns a list of dicts: [{start, end, trend}], where start/end are index labels (datetimes), trend is 'Uptrend', 'Downtrend', or 'Sideways'.
    """
    # Sort pivots by position in DataFrame
    pivots = sorted([(i, 'H') for i in pivot_high_indices] + [(i, 'L') for i in pivot_low_indices],
                    key=lambda x: df.index.get_loc(x[0]) if x[0] in df.index else -1)
    dt_trend = []
    dt_indices = []
    prev_high = prev_low = None
    for idx, typ in pivots:
        if typ == 'H':
            if prev_high is not None and prev_low is not None:
                if df['High'].loc[idx] > df['High'].loc[prev_high] and df['Low'].loc[prev_low] > df['Low'].loc[prev_low]:
                    dt_trend.append('Uptrend')
                elif df['High'].loc[idx] < df['High'].loc[prev_high] and df['Low'].loc[prev_low] < df['Low'].loc[prev_low]:
                    dt_trend.append('Downtrend')
                else:
                    dt_trend.append('Sideways')
            else:
                dt_trend.append('Sideways')
            dt_indices.append(idx)
            prev_high = idx
        elif typ == 'L':
            if prev_low is not None and prev_high is not None:
                if df['Low'].loc[idx] > df['Low'].loc[prev_low] and df['High'].loc[prev_high] > df['High'].loc[prev_high]:
                    dt_trend.append('Uptrend')
                elif df['Low'].loc[idx] < df['Low'].loc[prev_low] and df['High'].loc[prev_high] < df['High'].loc[prev_high]:
                    dt_trend.append('Downtrend')
                else:
                    dt_trend.append('Sideways')
            else:
                dt_trend.append('Sideways')
            dt_indices.append(idx)
            prev_low = idx
    # Build regions: each region is from dt_indices[i] to dt_indices[i+1] (or end of df)
    regions = []
    for i in range(len(dt_indices)):
        start_idx = dt_indices[i]
        end_idx = dt_indices[i+1] if i+1 < len(dt_indices) else df.index[-1]
        trend = dt_trend[i]
        regions.append({'start': start_idx, 'end': end_idx, 'trend': trend})
    return regions
