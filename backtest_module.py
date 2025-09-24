import backtrader as bt
import pandas as pd

class CustomStrategy(bt.Strategy):
    params = dict(
        custom_logic=None,  # function to be injected for custom logic
    )

    def __init__(self):
        self.order = None
        self.buyprice = None
        self.buycomm = None
        self.trades = []
        self.current_trade = None
        self.custom_logic = self.p.custom_logic

    def next(self):
        # User-defined logic should call self.buy(), self.sell(), etc.
        if self.custom_logic:
            self.custom_logic(self)

    def notify_order(self, order):
        if order.status in [order.Completed]:
            if order.isbuy():
                self.current_trade = {'entry': self.data.datetime.date(0), 'entry_price': order.executed.price}
            elif order.issell() and self.current_trade:
                self.current_trade['exit'] = self.data.datetime.date(0)
                self.current_trade['exit_price'] = order.executed.price
                self.current_trade['pnl'] = self.current_trade['exit_price'] - self.current_trade['entry_price']
                self.trades.append(self.current_trade)
                self.current_trade = None

    def stop(self):
        # Called at the end, can be used to summarize
        pass

def run_backtest(df, custom_logic):
    cerebro = bt.Cerebro()
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.addstrategy(CustomStrategy, custom_logic=custom_logic)
    cerebro.broker.setcash(100000.0)
    cerebro.run()
    strat = cerebro.runstrats[0][0]
    trades = strat.trades
    # Calculate stats
    n_profitable = sum(1 for t in trades if t['pnl'] > 0)
    n_loss = sum(1 for t in trades if t['pnl'] <= 0)
    returns = [t['pnl'] for t in trades]
    max_profit = max(returns) if returns else 0
    max_loss = min(returns) if returns else 0
    # Consecutive wins/losses
    cons_win = cons_loss = max_cons_win = max_cons_loss = 0
    last_win = None
    for pnl in returns:
        if pnl > 0:
            cons_win += 1
            cons_loss = 0
        else:
            cons_loss += 1
            cons_win = 0
        max_cons_win = max(max_cons_win, cons_win)
        max_cons_loss = max(max_cons_loss, cons_loss)
    return {
        'n_profitable': n_profitable,
        'n_loss': n_loss,
        'returns': returns,
        'max_profit': max_profit,
        'max_loss': max_loss,
        'max_consecutive_wins': max_cons_win,
        'max_consecutive_losses': max_cons_loss,
    }
