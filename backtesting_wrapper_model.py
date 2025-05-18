from backtesting import Backtest, Strategy
import pandas as pd
from datetime import timedelta
import os
from lstm_close import predict_stock  # ✅ Import your LSTM function

class BacktestingWrapper:
    def __init__(self, strategy=None, initial_cash=10000):
        self.strategy = strategy
        self.initial_cash = initial_cash

    def run_forecast_and_read(self, ticker, signal_time, interval):
        start_date = (signal_time - timedelta(days=332)).strftime("%Y-%m-%d")
        end_date = signal_time.strftime("%Y-%m-%d")

        print(f"🔮 Running LSTM forecast for {ticker}: {start_date} → {end_date}")
        try:
            predicted_price = predict_stock(ticker=ticker, start_date=start_date, end_date=end_date, interval=interval)
            return predicted_price
        except Exception as e:
            print(f"⚠️ Forecast error: {e}")
            return None

    def backtest(self, data, ticker="TSLA", interval="1h"):
        wrapper = self

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
                current_time = inner_self.data.index[-1]
                current_price = inner_self.data.Close[-1]
            
                # SELL logic when in a position
                if inner_self.position and inner_self.sell_signal[-1]:
                    print(f"🔻 Sell signal detected at {current_time}, running model...")
                    predicted_price = wrapper.run_forecast_and_read(ticker, current_time, interval)
                    if predicted_price is None:
                        return
                    print(f"📉 Current Price: {current_price:.2f}, Forecasted Price: {predicted_price:.2f}")
                    if predicted_price < current_price:
                        print(f"🔻 SELL Decision: Current={current_price:.2f}, Forecast={predicted_price:.2f}")
                        inner_self.position.close()
                        print(f"✅ Trade Executed: SOLD at {current_time} | Price: {current_price:.2f}")
                    else:
                        print(f"❌ No SELL executed: Forecast is not lower than current price.")
            
                # BUY logic when not in a position
                elif not inner_self.position and inner_self.buy_signal[-1]:
                    print(f"🔺 Buy signal detected at {current_time}, running model...")
                    predicted_price = wrapper.run_forecast_and_read(ticker, current_time, interval)
                    if predicted_price is None:
                        return
                    print(f"📈 Current Price: {current_price:.2f}, Forecasted Price: {predicted_price:.2f}")
                    if predicted_price > current_price:
                        size = inner_self.equity // current_price
                        if size > 0:
                            print(f"🔺 BUY Decision: Current={current_price:.2f}, Forecast={predicted_price:.2f}")
                            inner_self.buy(size=size)
                            print(f"✅ Trade Executed: BOUGHT {int(size)} units at {current_time} | Price: {current_price:.2f}")
                    else:
                        print(f"❌ No BUY executed: Forecast is not higher than current price.")


        try:
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
        final_equity = stats.get('Equity Final [$]', self.initial_cash)
        roi = ((final_equity - self.initial_cash) / self.initial_cash) * 100
        return {
            "Number of Trades": stats.get('# Trades', 0),
            "Return [%]": stats.get('Return [%]', 0),
            "Best Trade [$]": stats.get('Best Trade [%]', 0) * self.initial_cash / 100,
            "Worst Trade [$]": stats.get('Worst Trade [%]', 0) * self.initial_cash / 100,
            "ROI [%]": roi
        }