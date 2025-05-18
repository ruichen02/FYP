from strategies.macd import MACDStrategy
from strategies.bollinger import BollingerBandsStrategy
from strategies.cci import CCI_Strategy
from strategies.adx import ADXStrategy
from strategies.obv import OBVStrategy

from utils import (
    optimize_macd,
    optimize_bollinger_bands,
    optimize_cci,
    optimize_adx
)
from backtesting_wrapper import BacktestingWrapper

class StrategyProcessor:
    def __init__(self, strategy, data, min_length=None, max_length=None, min_threshold=None, max_threshold=None):
        self.strategy = strategy
        self.data = data
        self.min_length = min_length
        self.max_length = max_length
        self.min_threshold = min_threshold
        self.max_threshold = max_threshold


    def process_data(self):
        if isinstance(self.strategy, MACDStrategy):
            if self.min_length and self.max_length:
                params = optimize_macd(self.data, self.min_length, self.max_length)
                self.strategy = MACDStrategy(
                    fast_length=params['fast_length'],
                    slow_length=params['slow_length']
                )
            self.data = self.strategy.apply_strategy(self.data)

        elif isinstance(self.strategy, BollingerBandsStrategy):
            if self.min_length and self.max_length and self.min_std_dev and self.max_std_dev:
                params = optimize_bollinger_bands(
                    self.data, self.min_length, self.max_length,
                    self.min_std_dev, self.max_std_dev
                )
                self.strategy = BollingerBandsStrategy(
                    length=params['length'],
                    std_dev_multiplier=params['std_dev_multiplier']
                )
            self.data = self.strategy.apply_strategy(self.data)

        elif isinstance(self.strategy, CCI_Strategy):
            if self.min_length and self.max_length:
                params = optimize_cci(self.data, self.min_length, self.max_length)
                self.strategy = CCI_Strategy(length=params['length'])
            self.data = self.strategy.apply_strategy(self.data)

        elif isinstance(self.strategy, ADXStrategy):
            if self.min_length and self.max_length and self.min_threshold and self.max_threshold:
                params = optimize_adx(
                    self.data,
                    self.min_length,
                    self.max_length,
                    self.min_threshold,
                    self.max_threshold
                )
                self.strategy = ADXStrategy(
                    length=params['length'],
                    threshold=params['threshold']
                )
            self.data = self.strategy.apply_strategy(self.data)


        elif isinstance(self.strategy, OBVStrategy):
            self.data = self.strategy.apply_strategy(self.data)

        return self.data

    def backtest(self):
        backtest_wrapper = BacktestingWrapper(self.strategy)
        stats = backtest_wrapper.backtest(self.data)
        return backtest_wrapper.extract_statistics(stats)
