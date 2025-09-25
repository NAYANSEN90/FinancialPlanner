# FinancialPlanner: All-in-One Trading Tool

## Project Objectives

FinancialPlanner is a comprehensive trading platform designed to empower traders with robust scanning, evaluation, execution, and journaling capabilities. The tool is built for both discretionary and systematic traders, supporting the entire lifecycle of a trade:

### Key Features

- **Opportunity Scanning:**
  - Scans stocks for technical patterns (candlestick, chart patterns, etc.)
  - Detects actionable setups using advanced algorithms and multi-threaded scanning
  - Real-time progress and cancelable scans

- **Opportunity Evaluation & Grading:**
  - Evaluates detected opportunities using custom grading logic
  - Integrates technical indicators, trend analysis, and pattern quality scoring
  - Grades each opportunity for risk/reward, reliability, and fit with strategy

- **Execution Strategy:**
  - Suggests optimal entry, exit, and position sizing based on opportunity grade
  - Supports backtesting with custom strategies (via Backtrader)
  - Recommends best execution tactics (limit/market orders, scaling, etc.)

- **Trade Management:**
  - Monitors open trades and adapts execution as market conditions change
  - Implements trailing stops, partial exits, and dynamic risk management
  - Provides real-time trade status and actionable alerts

- **Trade Journal & Review:**
  - Automatically logs all trades, including rationale, execution details, and outcomes
  - Tracks what went right and what went wrong for continuous improvement
  - Generates performance reports and trade analytics

## Technology Stack
- Python, Streamlit, Plotly, pandas, yfinance, pandas-ta, Backtrader
- Modular architecture for scanning, pattern detection, strategy evaluation, and journaling
- Multi-threaded execution for fast, responsive UI and scanning

## Getting Started
1. Clone the repository and install dependencies
2. Run the Streamlit app (`app2.py`) to launch the trading dashboard
3. Configure your scanning, grading, and strategy preferences in the UI
4. Start scanning, evaluate opportunities, and manage trades—all in one place

## Vision
FinancialPlanner aims to be the trader's command center: from finding the next big opportunity, to executing with precision, to learning from every trade. Whether you're a beginner or a pro, this tool helps you trade smarter, faster, and with more confidence.

---

For more details, see the code documentation and UI walkthrough in the app.
