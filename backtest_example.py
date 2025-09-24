import pandas as pd
from backtest_module import run_backtest

def example_custom_logic(self):
    # Simple moving average crossover example
    if not hasattr(self, 'sma_fast'):
        self.sma_fast = self.datas[0].close.rolling(window=10).mean()
        self.sma_slow = self.datas[0].close.rolling(window=30).mean()
    if len(self.datas[0]) < 30:
        return
    if self.position.size == 0:
        if self.sma_fast[-1] > self.sma_slow[-1]:
            self.buy()
    else:
        if self.sma_fast[-1] < self.sma_slow[-1]:
            self.sell()

def main():
    # Load your OHLCV data as a pandas DataFrame
    df = pd.read_csv('EQUITY_L.csv')  # Replace with your data file
    # Ensure df has columns: Date, Open, High, Low, Close, Volume
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    # Run backtest
    results = run_backtest(df, example_custom_logic)
    print('Backtest Results:')
    for k, v in results.items():
        print(f'{k}: {v}')

if __name__ == '__main__':
    main()
