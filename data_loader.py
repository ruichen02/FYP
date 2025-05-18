import yfinance as yf
import pandas as pd
import os

FORECAST_DIR = "forecasts"  # Where forecast CSVs are saved

def fetch_data(ticker, start_date, end_date, interval, include_forecast=True):
    """
    Fetch adjusted stock data from Yahoo Finance and clean it.
    Optionally append forecasted data from CSV if available.

    Cleaning steps:
    - Adjusted prices for splits/dividends
    - Column name normalization
    - Forward/backward fill
    - Remove duplicate timestamps
    - Optional forecast merging with historical priority
    """
    print(f"📥 Fetching {interval} data for {ticker} from {start_date} to {end_date}...")

    data = yf.download(
        tickers=ticker,
        start=start_date,
        end=end_date,
        interval=interval,
        auto_adjust=True
    )

    if data.empty:
        raise ValueError(f"No data retrieved for {ticker} with interval '{interval}'.")

    # Flatten multi-index columns if present
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [' '.join(col).strip() for col in data.columns]

    # Clean column names (title case)
    data.columns = [col.replace(f" {ticker.upper()}", "").strip().title() for col in data.columns]

    expected_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing_cols = [col for col in expected_cols if col not in data.columns]
    if missing_cols:
        raise ValueError(f"Missing expected columns: {missing_cols}. Retrieved columns: {list(data.columns)}")

    # Drop duplicates and fill missing values
    data = data[expected_cols]
    data = data.ffill().bfill().dropna(subset=["Close"])
    data = data[~data.index.duplicated(keep="first")]

    # Reset index and standardize datetime column
    data = data.reset_index()
    if "Date" in data.columns:
        data.rename(columns={"Date": "Datetime"}, inplace=True)
    elif "Datetime" not in data.columns:
        raise ValueError("Expected a datetime column named 'Date' or 'Datetime' after reset_index()")

    # Normalize datetime
    data["Datetime"] = pd.to_datetime(data["Datetime"]).dt.tz_localize(None)
    data["Source"] = "Historical"

    # Include forecast data
    if include_forecast:
        forecast_path = os.path.join(FORECAST_DIR, f"{ticker}_forecast_combined.csv")
        if os.path.exists(forecast_path):
            forecast_df = pd.read_csv(forecast_path, parse_dates=["Datetime"])
            forecast_df["Datetime"] = forecast_df["Datetime"].dt.tz_localize(None)
            forecast_df["Source"] = "Forecast"

            # Combine with historical data, keeping historical in case of overlaps
            merged = pd.concat([forecast_df, data], ignore_index=True)
            merged = merged.drop_duplicates(subset="Datetime", keep="last")
            merged = merged.sort_values("Datetime").reset_index(drop=True)
            return merged

    return data.sort_values("Datetime").reset_index(drop=True)
