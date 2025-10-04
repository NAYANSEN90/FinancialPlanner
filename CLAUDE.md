# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FinancialPlanner is a comprehensive trading platform for scanning, analyzing, and managing stock trades. It provides real-time pattern detection, technical analysis, and portfolio management capabilities for NSE stocks.

## Running the Application

```bash
# Main Streamlit application (primary UI)
python -m streamlit run app2.py

# Alternative simple chart viewer
python -m streamlit run app.py

# Windows batch script (with virtual environment)
run_app.bat

# Individual modules for testing
python main.py              # NSE stock data fetching
python scanner.py           # Candlestick pattern scanning
python pattern_scanner.py   # Chart pattern scanning
python backtest_example.py  # Backtesting examples
```

## Project Architecture

### Core Modules
- **stock_data.py**: Stock data fetching and caching using yfinance API. Provides `fetch_stock_chart_data()` and stock symbol utilities.
- **scanner.py**: Candlestick pattern detection using pandas-ta. Scans all NSE stocks for technical patterns.
- **pattern_scanner.py**: Chart pattern detection (double tops, etc.) with multi-threaded scanning capabilities.
- **chart_patterns.py**: Pattern detection algorithms for flag/pole, double top/bottom, head & shoulders patterns.
- **analysis.py**: Dow Theory trend analysis and technical indicator calculations.
- **backtest_module.py**: Backtesting framework using Backtrader with custom strategy injection.

### UI Applications
- **app2.py**: Primary Streamlit application with advanced charting (Plotly), technical indicators, pattern scanning, and multi-threaded operations.
- **app.py**: Secondary Streamlit application with basic candlestick charts using mplfinance.

### Data Sources
- **EQUITY_L.csv**: NSE stock symbols and company names (primary stock list).
- **stock_list.csv**: Alternative stock list format.

### Key Features
- Multi-threaded pattern scanning with real-time progress and cancellation
- Interactive charts with technical indicators (EMA, RSI, Stochastic, Bollinger Bands)
- Pivot point detection and Dow Theory trend analysis
- Pattern detection for candlestick and chart patterns
- Backtesting capabilities with custom strategy logic
- Data caching for performance optimization

### Modular Architecture (New)
The codebase has been refactored into modular components:

#### UI Components (`ui/`)
- **session_state.py**: Centralized session state management for all applications
- **chart_renderer.py**: Chart rendering engines (Plotly for app2.py, mplfinance for app.py)
- **components/ema_controls.py**: Reusable EMA configuration components
- **components/toolbar.py**: Toolbar, date selection, and technical analysis panels

#### Services (`services/`)
- **technical_indicators.py**: Technical indicator calculations (RSI, Stochastic, EMAs, Bollinger Bands)
- **scanner_service.py**: Unified scanner service and UI for both candlestick and chart patterns

#### Benefits of Modularization
- **Reduced code duplication**: app2.py reduced from 720 to 81 lines (~89% reduction)
- **Improved maintainability**: Separated concerns with single responsibility principle
- **Enhanced testability**: Modular components can be unit tested independently
- **Easier feature addition**: New indicators and patterns can be added systematically
- **Shared components**: Both app.py and app2.py use common UI components 