from darts import TimeSeries
from darts.models import RNNModel
from darts.metrics import rmse, mape, mae
from darts.utils.likelihood_models import GaussianLikelihood
import yfinance as yf
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from datetime import datetime, timedelta
import os
import json

from pytorch_lightning.callbacks import EarlyStopping

# EarlyStopping callback
early_stopping = EarlyStopping(
    monitor="val_loss",
    patience=5,
    mode="min"
)

def predict_stock(ticker, start_date, end_date, interval="1h", use_best_config=True):
    df = yf.download(ticker, start=start_date, end=end_date, interval=interval)

    # ✅ Adjust OHLC based on Adj Close to correct for stock splits
    if 'Adj Close' in df.columns and 'Close' in df.columns:
        adjustment_factor = df["Adj Close"] / df["Close"]
        df["Close"] = df["Adj Close"]
        df["Open"] *= adjustment_factor
        df["High"] *= adjustment_factor
        df["Low"] *= adjustment_factor

    freq_map = {"15m": "15T", "30m": "30T", "1h": "H", "1d": "B"}
    df.index = pd.DatetimeIndex(df.index)

    if df.index.tz is None:
        df.index = df.index.tz_localize("US/Eastern")
    df.index = df.index.tz_convert("UTC").tz_localize(None)

    df = df.asfreq(freq_map.get(interval, "H"))
    df = df.ffill()

    if len(df) < 10:
        print(f"⚠️ Not enough data ({len(df)} rows) for model training. Skipping...")
        return None

    if df.empty:
        print("⚠️ No data returned. Try adjusting date range or checking ticker.")
        return None

    target_series = df[['Close']]
    covariates = df[['High', 'Open', 'Low', 'Volume']]

    train_size = int(len(df) * 0.8)
    train_target = target_series[:train_size]
    test_target = target_series[train_size:]
    train_covariates = covariates[:train_size]
    test_covariates = covariates[train_size:]

    target_scaler = MinMaxScaler()
    covariate_scaler = MinMaxScaler()

    train_target_scaled = pd.DataFrame(target_scaler.fit_transform(train_target), columns=['Close'], index=train_target.index)
    train_covariates_scaled = pd.DataFrame(covariate_scaler.fit_transform(train_covariates), columns=['High', 'Open', 'Low', 'Volume'], index=train_covariates.index)
    test_target_scaled = pd.DataFrame(target_scaler.transform(test_target), columns=['Close'], index=test_target.index)
    test_covariates_scaled = pd.DataFrame(covariate_scaler.transform(test_covariates), columns=['High', 'Open', 'Low', 'Volume'], index=test_covariates.index)

    last_index_time = df.index[-1]
    last_row = test_covariates_scaled.iloc[-1]
    future_index = pd.date_range(
        start=last_index_time + pd.tseries.frequencies.to_offset(freq_map.get(interval, "H")),
        periods=1,
        freq=freq_map.get(interval, "H")
    )
    future_rows = pd.DataFrame([last_row.values], columns=test_covariates_scaled.columns, index=future_index)
    test_covariates_scaled = pd.concat([test_covariates_scaled, future_rows])

    train_y = TimeSeries.from_dataframe(train_target_scaled, freq=freq_map.get(interval, "H"))
    test_y = TimeSeries.from_dataframe(test_target_scaled, freq=freq_map.get(interval, "H"))
    train_x = TimeSeries.from_dataframe(train_covariates_scaled, freq=freq_map.get(interval, "H"))
    test_x = TimeSeries.from_dataframe(test_covariates_scaled, freq=freq_map.get(interval, "H"))

    # ✅ Validation split (last 10% of training)
    val_split_idx = int(len(train_y) * 0.9)
    real_train_y = train_y[:val_split_idx]
    val_y = train_y[val_split_idx:]
    real_train_x = train_x[:val_split_idx]
    val_x = train_x[val_split_idx:]

    config_dir = "config"
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, f"{ticker.upper()}_close_lstm_config.json")

    if use_best_config and os.path.exists(config_path):
        with open(config_path, "r") as f:
            best_config = json.load(f)
        print(f"✅ Loaded best hyperparameters from {config_path}")

        model = RNNModel(
            model='LSTM',
            input_chunk_length=48,
            training_length=72,
            output_chunk_length=1,
            hidden_dim=32,
            n_rnn_layers=2,
            dropout=0.2,
            batch_size=64,
            n_epochs=100,
            optimizer_kwargs={"lr": 1e-3},
            likelihood=GaussianLikelihood(),
            random_state=42,
            model_name="LSTM_Model",
            log_tensorboard=False,
            force_reset=True,
            save_checkpoints=False,
            pl_trainer_kwargs={"accelerator": "gpu", "devices": 1, "callbacks": [early_stopping]}
        )

#, "callbacks": [early_stopping]
    else:
        print("⚠️ Using default hardcoded config.")
        model = RNNModel(
            model='LSTM',
            input_chunk_length=48,
            training_length=72,
            output_chunk_length=1,
            hidden_dim=32,
            n_rnn_layers=2,
            dropout=0.2,
            batch_size=64,
            n_epochs=100,
            optimizer_kwargs={"lr": 1e-3},
            likelihood=GaussianLikelihood(),
            random_state=42,
            model_name="LSTM_Model",
            log_tensorboard=False,
            force_reset=True,
            save_checkpoints=False,
            pl_trainer_kwargs={"accelerator": "gpu", "devices": 1, "callbacks": [early_stopping]}
        )

    model.fit(
        series=train_y,
        future_covariates=train_x,
        val_series=test_y,
        val_future_covariates=test_x,
        verbose=True
    )


    future_pred = model.predict(n=1, series=test_y, future_covariates=test_x)

    def inverse_transform_series(scaled_series):
        scaled_values = scaled_series.values().flatten()
        inverse_transformed = target_scaler.inverse_transform(scaled_values.reshape(-1, 1)).flatten()
        return TimeSeries.from_times_and_values(times=scaled_series.time_index, values=inverse_transformed)

    future_pred = inverse_transform_series(future_pred)
    predicted_price = float(future_pred.values().flatten()[0])

    print(f"\n📈 Predicted next close price for {ticker}: ${predicted_price:.2f}")
    return predicted_price
