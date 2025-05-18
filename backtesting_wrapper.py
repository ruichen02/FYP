from backtesting import Backtest, Strategy

class BacktestingWrapper:
    def __init__(self, strategy, initial_cash=10000):
        self.strategy = strategy
        self.initial_cash = initial_cash

    def backtest(self, data):
        class CustomStrategy(Strategy):
            def init(inner_self):
                if 'CommonBuySignal' in data.columns:
                    inner_self.buy_signal = inner_self.I(lambda: data['CommonBuySignal'])
                else:
                    inner_self.buy_signal = inner_self.I(lambda: data['BuySignal'])
    
                if 'CommonSellSignal' in data.columns:
                    inner_self.sell_signal = inner_self.I(lambda: data['CommonSellSignal'])
                else:
                    inner_self.sell_signal = inner_self.I(lambda: data['SellSignal'])
    
            def next(inner_self):
                if inner_self.position:
                    if inner_self.sell_signal[-1]:
                        inner_self.position.close()
                else:
                    if inner_self.buy_signal[-1]:
                        price = inner_self.data.Close[-1]
                        size = inner_self.equity // price
                        inner_self.buy(size=size)
    
        try:
            # ✅ Ensure proper DateTime index
            data = data.copy()
            if "Datetime" in data.columns:
                data = data.set_index("Datetime")
    
            bt = Backtest(data, CustomStrategy, cash=self.initial_cash, commission=0.002)
            stats = bt.run()
    
        except ZeroDivisionError:
            stats = {
                "# Trades": 0,
                "Equity Final [$]": self.initial_cash,
                "Return [%]": 0,
                "Sharpe Ratio": 0
            }
    
        return stats


    def extract_statistics(self, stats):
        return {
            "Number of Trades": stats.get('# Trades', 0),
            "Return [%]": stats.get('Return [%]',0),
            "Best Trade [$]": stats.get('Best Trade [%]', 0) * self.initial_cash / 100,
            "Worst Trade [$]": stats.get('Worst Trade [%]', 0) * self.initial_cash / 100
        }