import numpy as np
import pandas as pd

class BollingerBandsStrategy:

    def __init__(self, length=20, std_dev_multiplier=2):
        # Validate and convert length to integer
        self.length = int(length) if length > 0 else 20  # Default to 20 if invalid
        self.std_dev_multiplier = float(std_dev_multiplier)

    def calculate_bollinger_bands(self, series):
        """
        Calculate Bollinger Bands for a given price series
        
        Parameters:
        series (pandas.Series): Price series to calculate bands for
        
        Returns:
        tuple: (middle_band, upper_band, lower_band)
        """
        # Convert to pandas Series if not already
        series = pd.Series(series)
        
        # Calculate rolling mean and standard deviation
        rolling_mean = series.rolling(window=int(self.length), min_periods=1).mean()
        rolling_std = series.rolling(window=int(self.length), min_periods=1).std()
        
        # Calculate bands
        middle_band = rolling_mean
        upper_band = rolling_mean + (rolling_std * self.std_dev_multiplier)
        lower_band = rolling_mean - (rolling_std * self.std_dev_multiplier)
        
        return middle_band, upper_band, lower_band

    def apply_strategy(self, df):
        """
        Apply Bollinger Bands strategy to the dataframe
        
        Parameters:
        df (pandas.DataFrame): DataFrame with OHLC data
        
        Returns:
        pandas.DataFrame: DataFrame with Bollinger Bands and signals
        """
        # Create a copy to avoid modifying original data
        df = df.copy()
        
        # Calculate Bollinger Bands
        middle_band, upper_band, lower_band = self.calculate_bollinger_bands(df['Close'])
        
        # Add bands to dataframe
        df['MiddleBand'] = middle_band
        df['UpperBand'] = upper_band
        df['LowerBand'] = lower_band
        
        # Generate trading signals
        df['BuySignal'] = (df['Close'] < df['LowerBand'])
        df['SellSignal'] = (df['Close'] > df['UpperBand'])
        
        return df