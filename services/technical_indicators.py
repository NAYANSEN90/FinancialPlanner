import pandas as pd
import numpy as np

class TechnicalIndicators:
    """Service class for computing technical indicators"""

    @staticmethod
    def compute_rsi(series, period=14):
        """
        Compute Relative Strength Index (RSI)

        Args:
            series: Price series (typically Close prices)
            period: RSI period (default 14)

        Returns:
            pandas.Series: RSI values
        """
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def compute_stochastic(df, k_period=14, d_period=3, smooth_k=3):
        """
        Compute Stochastic oscillator (%K and %D)

        Args:
            df: DataFrame with High, Low, Close columns
            k_period: %K period
            d_period: %D period
            smooth_k: Smoothing period for %K

        Returns:
            tuple: (percent_k, percent_d) pandas Series
        """
        low_min = df['Low'].rolling(window=k_period, min_periods=1).min()
        high_max = df['High'].rolling(window=k_period, min_periods=1).max()
        percent_k = 100 * (df['Close'] - low_min) / (high_max - low_min)
        percent_k = percent_k.rolling(window=smooth_k, min_periods=1).mean()
        percent_d = percent_k.rolling(window=d_period, min_periods=1).mean()
        return percent_k, percent_d

    @staticmethod
    def compute_ema(series, period):
        """
        Compute Exponential Moving Average

        Args:
            series: Price series
            period: EMA period

        Returns:
            pandas.Series: EMA values
        """
        return series.ewm(span=period, adjust=False).mean()

    @staticmethod
    def compute_bollinger_bands(series, period=20, std_dev=2):
        """
        Compute Bollinger Bands

        Args:
            series: Price series (typically Close prices)
            period: Moving average period
            std_dev: Standard deviation multiplier

        Returns:
            tuple: (middle_band, upper_band, lower_band)
        """
        middle_band = series.rolling(window=period).mean()
        std = series.rolling(window=period).std()
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        return middle_band, upper_band, lower_band

    @staticmethod
    def find_pivots(series, window=3, mode='high'):
        """
        Find pivot points (local maxima or minima)

        Args:
            series: Price series
            window: Window size for pivot detection
            mode: 'high' for pivot highs, 'low' for pivot lows

        Returns:
            list: Indices of pivot points
        """
        pivots = []
        for i in range(window, len(series) - window):
            if mode == 'high':
                if series.iloc[i] == max(series[i-window:i+window+1]):
                    pivots.append(i)
            else:
                if series.iloc[i] == min(series[i-window:i+window+1]):
                    pivots.append(i)
        return pivots

    @staticmethod
    def compute_volume_ma(volume_series, period=20):
        """
        Compute Volume Moving Average

        Args:
            volume_series: Volume data
            period: Moving average period

        Returns:
            pandas.Series: Volume moving average
        """
        return volume_series.rolling(window=period).mean()

class TechnicalAnalysis:
    """Higher-level technical analysis functions"""

    @staticmethod
    def get_all_indicators(df, ema_periods=None):
        """
        Compute all standard technical indicators for a DataFrame

        Args:
            df: OHLCV DataFrame
            ema_periods: List of EMA periods to compute

        Returns:
            dict: Dictionary containing all computed indicators
        """
        if ema_periods is None:
            ema_periods = [20, 50]

        indicators = {}

        # RSI
        indicators['rsi'] = TechnicalIndicators.compute_rsi(df['Close'])

        # Stochastic
        indicators['stoch_k'], indicators['stoch_d'] = TechnicalIndicators.compute_stochastic(df)

        # EMAs
        indicators['emas'] = {}
        for period in ema_periods:
            indicators['emas'][period] = TechnicalIndicators.compute_ema(df['Close'], period)

        # Bollinger Bands
        bb_middle, bb_upper, bb_lower = TechnicalIndicators.compute_bollinger_bands(df['Close'])
        indicators['bollinger'] = {
            'middle': bb_middle,
            'upper': bb_upper,
            'lower': bb_lower
        }

        # Volume MA
        indicators['volume_ma'] = TechnicalIndicators.compute_volume_ma(df['Volume'])

        # Pivots
        indicators['pivot_highs'] = TechnicalIndicators.find_pivots(df['High'], mode='high')
        indicators['pivot_lows'] = TechnicalIndicators.find_pivots(df['Low'], mode='low')

        return indicators

    @staticmethod
    def is_oversold(rsi_value, threshold=30):
        """Check if RSI indicates oversold condition"""
        return rsi_value < threshold

    @staticmethod
    def is_overbought(rsi_value, threshold=70):
        """Check if RSI indicates overbought condition"""
        return rsi_value > threshold

    @staticmethod
    def is_stoch_oversold(stoch_k, stoch_d, threshold=20):
        """Check if Stochastic indicates oversold condition"""
        return stoch_k < threshold and stoch_d < threshold

    @staticmethod
    def is_stoch_overbought(stoch_k, stoch_d, threshold=80):
        """Check if Stochastic indicates overbought condition"""
        return stoch_k > threshold and stoch_d > threshold