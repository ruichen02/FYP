import yfinance as yf
import pandas as pd
import numpy as np
from itertools import product
from strategies.macd import MACDStrategy
from strategies.bollinger import BollingerBandsStrategy
from strategies.cci import CCI_Strategy
from strategies.adx import ADXStrategy
from strategies.obv import OBVStrategy
from data_loader import fetch_data

from backtesting_wrapper import BacktestingWrapper

# Simple in-memory cache
parameter_cache = {}

def combine_signals(data, selected_strategies):
    data = data.copy()
    data['CommonBuySignal'] = True
    data['CommonSellSignal'] = True

    for strategy in selected_strategies:
        buy_col = f'BuySignal{strategy}'
        sell_col = f'SellSignal{strategy}'
        if buy_col in data.columns:
            data['CommonBuySignal'] &= data[buy_col]
        if sell_col in data.columns:
            data['CommonSellSignal'] &= data[sell_col]

    return data

def optimize_macd(df, min_length, max_length):
    key = ("MACD", min_length, max_length)
    if key in parameter_cache:
        return parameter_cache[key]

    results = []
    for fast, slow in product(range(min_length, max_length + 1), repeat=2):
        if fast < slow:
            strategy = MACDStrategy(fast, slow)
            df_with_strategy = strategy.apply_strategy(df.copy())
            stats = BacktestingWrapper(strategy).backtest(df_with_strategy)
            results.append({
                'fast_length': fast,
                'slow_length': slow,
                'return': stats['Return [%]']
            })

    top_results = sorted(results, key=lambda x: x['return'], reverse=True)[:5]

    print("\n[MACD] Top 5 Parameter Combinations:")
    print("{:<12} {:<12} {:<10}".format("Fast Length", "Slow Length", "Return [%]"))
    for res in top_results:
        print("{:<12} {:<12} {:<10.2f}".format(res['fast_length'], res['slow_length'], res['return']))

    best = top_results[0] if top_results else {'fast_length': min_length, 'slow_length': min_length + 1}
    parameter_cache[key] = best
    return best


def optimize_bollinger_bands(df, min_length, max_length, min_std, max_std):
    results = []
    for length in range(min_length, max_length + 1):
        for std in np.arange(min_std, max_std + 0.1, 0.1):
            std = round(std, 2)
            strategy = BollingerBandsStrategy(length=length, std_dev_multiplier=std)
            df_with_strategy = strategy.apply_strategy(df.copy())
            stats = BacktestingWrapper(strategy).backtest(df_with_strategy)
            if stats.get('Return [%]', 0) > 0:
                results.append({
                    'length': length,
                    'std_dev_multiplier': std,
                    'return': stats['Return [%]']
                })

    top_results = sorted(results, key=lambda x: x['return'], reverse=True)[:5]

    print("\n[BollingerBands] Top 5 Parameter Combinations:")
    print("{:<10} {:<20} {:<10}".format("Length", "Std Dev Multiplier", "Return [%]"))
    for res in top_results:
        print("{:<10} {:<20} {:<10.2f}".format(res['length'], res['std_dev_multiplier'], res['return']))

    return top_results[0] if top_results else {'length': min_length, 'std_dev_multiplier': min_std}


def optimize_cci(df, min_length, max_length):
    results = []
    for length in range(min_length, max_length + 1):
        strategy = CCI_Strategy(length=length)
        df_with_strategy = strategy.apply_strategy(df.copy())
        stats = BacktestingWrapper(strategy).backtest(df_with_strategy)
        results.append({
            'length': length,
            'return': stats['Return [%]']
        })

    top_results = sorted(results, key=lambda x: x['return'], reverse=True)[:5]

    print("\n[CCI] Top 5 Parameter Combinations:")
    print("{:<10} {:<10}".format("Length", "Return [%]"))
    for res in top_results:
        print("{:<10} {:<10.2f}".format(res['length'], res['return']))

    return top_results[0] if top_results else {'length': min_length}


def optimize_adx(df, min_length, max_length, min_threshold, max_threshold):
    results = []
    for length in range(min_length, max_length + 1):
        for threshold in range(min_threshold, max_threshold + 1):
            strategy = ADXStrategy(length=length, threshold=threshold)
            df_with_strategy = strategy.apply_strategy(df.copy())
            stats = BacktestingWrapper(strategy).backtest(df_with_strategy)
            results.append({
                'length': length,
                'threshold': threshold,
                'return': stats['Return [%]']
            })

    top_results = sorted(results, key=lambda x: x['return'], reverse=True)[:5]

    print("\n[ADX] Top 5 Parameter Combinations:")
    print("{:<10} {:<12} {:<10}".format("Length", "Threshold", "Return [%]"))
    for res in top_results:
        print("{:<10} {:<12} {:<10.2f}".format(res['length'], res['threshold'], res['return']))

    return top_results[0] if top_results else {'length': min_length, 'threshold': min_threshold}

