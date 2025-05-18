import pandas as pd

class MACDStrategy:
    def __init__(self, fast_length=12, slow_length=26, signal_length=9):
        self.fast_length = fast_length
        self.slow_length = slow_length
        self.signal_length = signal_length

    def ema(self, series, length):
        series = pd.Series(series)
        ma1 = series.ewm(span=length).mean()
        ma2 = ma1.ewm(span=length).mean()
        return (2 * ma1 - ma2).values

    def calculate_signal(self, macd, length):
        macd = pd.Series(macd)
        emasig1 = macd.ewm(span=length).mean()
        emasig2 = emasig1.ewm(span=length).mean()
        return (2 * emasig1 - emasig2).values

    def apply_strategy(self, df):
        close = df['Close']
        df['MACDFast'] = self.ema(close, self.fast_length)
        df['MACDSlow'] = self.ema(close, self.slow_length)
        df['MACD'] = df['MACDFast'] - df['MACDSlow']
        df['Signal'] = self.calculate_signal(df['MACD'], self.signal_length)
        df['Histogram'] = df['MACD'] - df['Signal']
        
        # Logic-based Buy and Sell Signals
        df['BuySignal'] = ((df['MACD'] > df['Signal']) & (df['MACD'].shift(1) <= df['Signal'].shift(1)))
        df['SellSignal'] = ((df['MACD'] < df['Signal']) & (df['MACD'].shift(1) >= df['Signal'].shift(1)))

        return df