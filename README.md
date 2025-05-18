# FYP
# 📊 AI-Driven Stock Trading Strategy with LSTM and Technical Indicators

## 🧠 Project Overview
This project develops an AI-powered trading bot that integrates **Long Short-Term Memory (LSTM)** models with classical **technical indicators** to enhance stock trading strategies. The system is tested using hourly stock data for **Apple Inc. (AAPL)** from April 2024 to April 2025.

---

## 🎯 Objectives
1. **Minimize lag** in traditional technical indicators using predictive LSTM models.
2. **Optimize multi-indicator strategies** through parameter tuning and ensemble combinations.
3. **Backtest and evaluate** the performance of AI-enhanced strategies against traditional methods.

---

## 🛠️ Methodology

### 1. **Data Collection**
- Extract historical stock data from Yahoo Finance (AAPL, 1-hour interval).

### 2. **Data Preprocessing**
- Clean missing values.
- Normalize and adjust for splits/dividends.
- Remove duplicates and standardize timestamps.

### 3. **Feature Engineering**
- Compute the following indicators:
  - MACD (momentum/trend)
  - ADX (trend strength)
  - CCI (momentum/overbought-oversold)
  - Bollinger Bands (volatility)
  - OBV (volume-based)

### 4. **Parameter Optimization**
- Tune each indicator's parameters to maximize return in backtesting.

### 5. **LSTM Integration**
- Predict the **next hour’s stock price** using LSTM.
- Use **adaptive threshold logic**:
  - Execute **buy** if: `Δ > threshold` AND `predicted > current`
  - Execute **sell** if: `Δ < -threshold` AND `predicted < current`

### 6. **Backtesting and Evaluation**
- Evaluate using:
  - Total Return
  - Best/Worst Trade
  - Number of Trades
  - MAE, RMSE, MAPE, R²

---

## 📈 Results Summary

| Strategy                | Return (Traditional) | Return (LSTM) | Worst Trade (LSTM) | Best Trade (LSTM) |
|------------------------|----------------------|---------------|--------------------|-------------------|
| MACD                   | 9.22%                | 25.57%        | -$263.09           | $616.62           |
| ADX                    | -0.81%               | 31.42%        | -$0.62             | $1095.88          |
| MACD + ADX + OBV       | 9.38%                | **46.15%**    | **$205.19**        | **$3324.77**      |
| CCI + ADX + OBV        | 34.03%               | 34.64%        | $1171.55           | $2074.52          |

> 💡 LSTM-based strategies consistently outperformed traditional ones in both return and risk reduction.

---

## ✅ Conclusion
By combining **LSTM-based time series forecasting** with **optimized technical indicators**, this project:
- Enhances **predictive power** in volatile markets.
- Minimizes **emotional and reactive trading**.
- Improves **profitability and downside protection**, especially with multi-indicator strategies.

This demonstrates the viability of LSTM-enhanced strategies for real-time algorithmic trading systems.
