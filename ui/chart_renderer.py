import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import mplfinance as mpf

from stock_data import fetch_stock_chart_data, _stock_data_cache
from services.technical_indicators import TechnicalIndicators
from analysis import determine_dow_theory_regions

class PlotlyChartRenderer:
    """Chart renderer using Plotly for interactive charts"""

    @staticmethod
    def render(symbol, interval, start_date, end_date, show_bollinger=False,
               show_pivot_highs=False, show_pivot_lows=False, ema_list=None):
        """
        Render interactive Plotly chart with technical indicators

        Args:
            symbol: Stock symbol
            interval: Time interval
            start_date: Start date
            end_date: End date
            show_bollinger: Whether to show Bollinger Bands
            show_pivot_highs: Whether to show pivot highs
            show_pivot_lows: Whether to show pivot lows
            ema_list: List of EMA configurations
        """
        if ema_list is None:
            ema_list = st.session_state.get('ema_list', [])

        # Fetch data
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        chart_data = fetch_stock_chart_data(symbol, start_date=start_str, end_date=end_str, interval=interval)

        # Get full cached data for indicators
        cache_key = f"{symbol}_{interval}"
        full_data = _stock_data_cache.get(cache_key, chart_data)

        # Handle large datasets with windowing
        MAX_CANDLES = 20000
        if len(chart_data) > MAX_CANDLES:
            chart_data_window = PlotlyChartRenderer._handle_windowing(chart_data, MAX_CANDLES)
        else:
            chart_data_window = chart_data
            st.session_state['window_start_idx'] = 0

        if chart_data_window.empty:
            st.warning("No chart data available for this stock.")
            return

        # Compute indicators
        rsi_full = TechnicalIndicators.compute_rsi(full_data['Close'])
        rsi = rsi_full.loc[chart_data_window.index]
        stoch_k, stoch_d = TechnicalIndicators.compute_stochastic(chart_data_window, 14, 3, 3)

        # Create subplots
        fig = make_subplots(
            rows=4, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.04,
            row_heights=[0.5, 0.15, 0.15, 0.2],
            subplot_titles=(f"{symbol} Candlestick Chart", f"{symbol} RSI (14)", "Stochastic (14,3,3)", "Volume")
        )

        # Add candlestick chart
        PlotlyChartRenderer._add_candlestick_trace(fig, chart_data_window)

        # Add EMA overlays
        PlotlyChartRenderer._add_ema_traces(fig, chart_data_window, full_data, ema_list)

        # Add Bollinger Bands
        if show_bollinger:
            PlotlyChartRenderer._add_bollinger_bands(fig, chart_data_window, full_data)

        # Add pivots
        if show_pivot_highs or show_pivot_lows:
            PlotlyChartRenderer._add_pivot_points(fig, chart_data_window, show_pivot_highs, show_pivot_lows)

        # Add Dow Theory regions
        PlotlyChartRenderer._add_dow_theory_regions(fig, chart_data_window, show_pivot_highs, show_pivot_lows)

        # Add RSI
        PlotlyChartRenderer._add_rsi_trace(fig, chart_data_window, rsi)

        # Add Stochastic
        PlotlyChartRenderer._add_stochastic_traces(fig, chart_data_window, stoch_k, stoch_d)

        # Add Volume
        PlotlyChartRenderer._add_volume_traces(fig, chart_data_window, full_data)

        # Update layout
        PlotlyChartRenderer._update_layout(fig)

        # Display chart
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "scrollZoom": True,
                "displayModeBar": True
            }
        )

    @staticmethod
    def _handle_windowing(chart_data, max_candles):
        """Handle windowing for large datasets"""
        window_start = st.session_state.get('window_start_idx', 0)
        window_end = window_start + max_candles
        if window_end > len(chart_data):
            window_end = len(chart_data)
            window_start = window_end - max_candles

        # Navigation controls
        nav_col1, _, nav_col3 = st.columns([1, 2, 1])
        with nav_col1:
            def navigate_older():
                st.session_state['window_start_idx'] = max(0, window_start - max_candles//2)

            st.button('← Older', key='older_candles', on_click=navigate_older)
        with nav_col3:
            def navigate_newer():
                st.session_state['window_start_idx'] = min(len(chart_data) - max_candles, window_start + max_candles//2)

            st.button('Newer →', key='newer_candles', on_click=navigate_newer)

        return chart_data.iloc[window_start:window_end]

    @staticmethod
    def _add_candlestick_trace(fig, chart_data_window):
        """Add candlestick trace to figure"""
        fig.add_trace(go.Candlestick(
            x=chart_data_window.index,
            open=chart_data_window['Open'],
            high=chart_data_window['High'],
            low=chart_data_window['Low'],
            close=chart_data_window['Close'],
            name='Candlestick'
        ), row=1, col=1)

    @staticmethod
    def _add_ema_traces(fig, chart_data_window, full_data, ema_list):
        """Add EMA traces to figure"""
        color_cycle = ['#e377c2', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']

        for i, ema in enumerate(ema_list):
            if ema.get('visible', False):
                ema_series_full = TechnicalIndicators.compute_ema(full_data['Close'], ema['period'])
                ema_series = ema_series_full.loc[chart_data_window.index]
                fig.add_trace(go.Scatter(
                    x=chart_data_window.index,
                    y=ema_series,
                    mode='lines',
                    name=f'EMA {ema["period"]}',
                    line=dict(color=color_cycle[i % len(color_cycle)], width=2)
                ), row=1, col=1)

    @staticmethod
    def _add_bollinger_bands(fig, chart_data_window, full_data):
        """Add Bollinger Bands to figure"""
        bb_middle, bb_upper, bb_lower = TechnicalIndicators.compute_bollinger_bands(full_data['Close'])

        # Filter for current window
        bb_upper_window = bb_upper.loc[chart_data_window.index]
        bb_lower_window = bb_lower.loc[chart_data_window.index]

        fig.add_trace(go.Scatter(
            x=chart_data_window.index,
            y=bb_upper_window,
            mode='lines',
            name='BB Upper',
            line=dict(color='blue', width=1, dash='dot'),
            opacity=0.7
        ), row=1, col=1)

        fig.add_trace(go.Scatter(
            x=chart_data_window.index,
            y=bb_lower_window,
            mode='lines',
            name='BB Lower',
            line=dict(color='blue', width=1, dash='dot'),
            opacity=0.7
        ), row=1, col=1)

    @staticmethod
    def _add_pivot_points(fig, chart_data_window, show_pivot_highs, show_pivot_lows):
        """Add pivot points to figure"""
        pivot_marker_size = 16

        if show_pivot_highs:
            pivot_high_indices = TechnicalIndicators.find_pivots(chart_data_window['High'], window=3, mode='high')
            if pivot_high_indices:
                fig.add_trace(go.Scatter(
                    x=chart_data_window.index[pivot_high_indices],
                    y=chart_data_window['High'].iloc[pivot_high_indices],
                    mode='markers',
                    marker=dict(symbol='triangle-up', color='red', size=pivot_marker_size),
                    name='Pivot High',
                    hoverinfo='x+y+name'
                ), row=1, col=1)

        if show_pivot_lows:
            pivot_low_indices = TechnicalIndicators.find_pivots(chart_data_window['Low'], window=3, mode='low')
            if pivot_low_indices:
                fig.add_trace(go.Scatter(
                    x=chart_data_window.index[pivot_low_indices],
                    y=chart_data_window['Low'].iloc[pivot_low_indices],
                    mode='markers',
                    marker=dict(symbol='triangle-down', color='green', size=pivot_marker_size),
                    name='Pivot Low',
                    hoverinfo='x+y+name'
                ), row=1, col=1)

    @staticmethod
    def _add_dow_theory_regions(fig, chart_data_window, show_pivot_highs, show_pivot_lows):
        """Add Dow Theory regions to figure"""
        show_dow_theory = st.session_state.get('show_dow_theory', False)

        if show_dow_theory and (show_pivot_highs or show_pivot_lows):
            pivot_high_indices = TechnicalIndicators.find_pivots(chart_data_window['High'], window=3, mode='high') if show_pivot_highs else []
            pivot_low_indices = TechnicalIndicators.find_pivots(chart_data_window['Low'], window=3, mode='low') if show_pivot_lows else []

            if pivot_high_indices or pivot_low_indices:
                pivot_high_dates = chart_data_window.index[pivot_high_indices] if pivot_high_indices else []
                pivot_low_dates = chart_data_window.index[pivot_low_indices] if pivot_low_indices else []

                regions = determine_dow_theory_regions(chart_data_window, pivot_high_dates, pivot_low_dates)
                region_colors = {'Uptrend': 'rgba(0,200,0,0.08)', 'Downtrend': 'rgba(200,0,0,0.08)', 'Sideways': 'rgba(120,120,120,0.08)'}

                for region in regions:
                    fig.add_vrect(
                        x0=region['start'], x1=region['end'],
                        fillcolor=region_colors[region['trend']],
                        opacity=0.25,
                        layer="below",
                        line_width=0,
                        row=1, col=1
                    )

    @staticmethod
    def _add_rsi_trace(fig, chart_data_window, rsi):
        """Add RSI trace to figure"""
        fig.add_trace(go.Scatter(
            x=chart_data_window.index,
            y=rsi,
            mode='lines',
            name='RSI',
            line=dict(color='purple', width=2)
        ), row=2, col=1)

        fig.add_hline(y=60, line_dash="dash", line_color="red", annotation_text="Overbought", annotation_position="top right", row=2)
        fig.add_hline(y=40, line_dash="dash", line_color="green", annotation_text="Oversold", annotation_position="bottom right", row=2)

    @staticmethod
    def _add_stochastic_traces(fig, chart_data_window, stoch_k, stoch_d):
        """Add Stochastic traces to figure"""
        fig.add_trace(go.Scatter(
            x=chart_data_window.index,
            y=stoch_k,
            mode='lines',
            name='%K',
            line=dict(color='blue', width=2)
        ), row=3, col=1)

        fig.add_trace(go.Scatter(
            x=chart_data_window.index,
            y=stoch_d,
            mode='lines',
            name='%D',
            line=dict(color='orange', width=2, dash='dash')
        ), row=3, col=1)

        fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="Overbought", annotation_position="top right", row=3)
        fig.add_hline(y=20, line_dash="dash", line_color="green", annotation_text="Oversold", annotation_position="bottom right", row=3)

    @staticmethod
    def _add_volume_traces(fig, chart_data_window, full_data):
        """Add volume traces to figure"""
        fig.add_trace(go.Bar(
            x=chart_data_window.index,
            y=chart_data_window['Volume'],
            name='Volume',
            marker_color='rgba(50,50,150,0.7)',
            opacity=0.4
        ), row=4, col=1)

        vol_ma20 = TechnicalIndicators.compute_volume_ma(full_data['Volume'], 20)
        vol_ma20_window = vol_ma20.loc[chart_data_window.index]
        fig.add_trace(go.Scatter(
            x=chart_data_window.index,
            y=vol_ma20_window,
            mode='lines',
            name='Volume MA 20',
            line=dict(color='orange', width=2, dash='dash')
        ), row=4, col=1)

    @staticmethod
    def _update_layout(fig):
        """Update figure layout"""
        fig.update_layout(
            height=1200,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='left',
                x=0
            ),
            xaxis_rangeslider_visible=False,
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
            ),
            yaxis2=dict(
                title='RSI',
                range=[0, 100],
            ),
            yaxis3=dict(
                title='Stochastic',
                range=[0, 100],
            ),
            yaxis4=dict(
                title='Volume',
                showgrid=False,
            ),
            margin=dict(l=40, r=40, t=40, b=40)
        )

class MPLFinanceChartRenderer:
    """Chart renderer using mplfinance for static charts (app.py compatibility)"""

    @staticmethod
    def prepare_mpf_data(data):
        """Clean and prepare DataFrame for mplfinance plotting"""
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = data.copy()

        # Ensure index is datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        if not pd.api.types.is_datetime64_any_dtype(df.index):
            df.index = pd.to_datetime(df.index)

        # Only keep required columns
        df = df[required_cols]

        # Ensure all columns are numeric
        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=required_cols)
        return df

    @staticmethod
    def render(data, symbol, ema_list=None):
        """Render mplfinance chart"""
        if ema_list is None:
            ema_list = st.session_state.get('ema_list', [])

        # Clean and prepare data
        cleaned = MPLFinanceChartRenderer.prepare_mpf_data(data)
        if cleaned is None or cleaned.empty:
            st.warning("Data is not suitable for candlestick plotting.")
            return

        # Prepare EMA overlays
        addplots = []
        legend_labels = []
        legend_colors = []
        for i, ema in enumerate(ema_list):
            if ema.get('visible', False):
                color = f'C{i}'
                ema_series = TechnicalIndicators.compute_ema(cleaned['Close'], ema['period'])
                addplots.append(mpf.make_addplot(ema_series, color=color, width=1.5, ylabel=f'EMA {ema["period"]}'))
                legend_labels.append(f'EMA {ema["period"]}')
                legend_colors.append(color)

        # Plot candlestick and volume
        fig, axes = mpf.plot(
            cleaned,
            type='candle',
            style='charles',
            volume=True,
            title=f'{symbol} Candlestick Chart',
            returnfig=True,
            figratio=(10, 6),
            figscale=1.1,
            addplot=addplots if addplots else None
        )

        # Add legend for EMAs
        if legend_labels and hasattr(axes, '__getitem__'):
            import matplotlib.patches as mpatches
            price_ax = axes[0] if isinstance(axes, (list, tuple)) else axes
            handles = [mpatches.Patch(color=legend_colors[i], label=legend_labels[i]) for i in range(len(legend_labels))]
            price_ax.legend(handles=handles, loc='upper left')

        st.pyplot(fig)