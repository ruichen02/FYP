import numpy as np
import pandas as pd

class CCI_Strategy:
    def __init__(self, length=20, constant=0.015):
        """
        Initialize CCI Strategy with parameters
        
        Parameters:
        length (int): Length of the lookback period (must be > 0)
        constant (float): Scaling constant (typically 0.015)
        """
        # Validate and convert parameters
        self.length = int(length) if length > 0 else 20  # Default to 20 if invalid
        self.constant = float(constant) if constant > 0 else 0.015  # Default to 0.015 if invalid

    def typical_price(self, high, low, close):
        """
        Calculate Typical Price
        
        Parameters:
        high (pandas.Series): High prices
        low (pandas.Series): Low prices
        close (pandas.Series): Close prices
        
        Returns:
        pandas.Series: Typical prices
        """
        # Convert inputs to pandas Series if they aren't already
        high = pd.Series(high)
        low = pd.Series(low)
        close = pd.Series(close)
        
        return (high + low + close) / 3

    def sma(self, typical_price):
        """
        Calculate Simple Moving Average (SMA) of the Typical Price
        
        Parameters:
        typical_price (pandas.Series): Typical price series
        
        Returns:
        pandas.Series: Simple Moving Average
        """
        return typical_price.rolling(window=int(self.length), min_periods=1).mean()

    def mean_deviation(self, typical_price, sma):
        """
        Calculate Mean Deviation
        
        Parameters:
        typical_price (pandas.Series): Typical price series
        sma (pandas.Series): Simple Moving Average series
        
        Returns:
        pandas.Series: Mean Deviation
        """
        return (typical_price - sma).abs().rolling(window=int(self.length), min_periods=1).mean()

    def calculate_cci(self, close, high, low):
        """
        Calculate Commodity Channel Index (CCI)
        
        Parameters:
        close (pandas.Series): Close prices
        high (pandas.Series): High prices
        low (pandas.Series): Low prices
        
        Returns:
        pandas.Series: CCI values
        """
        try:
            typical_price = self.typical_price(high, low, close)
            sma = self.sma(typical_price)
            mean_deviation = self.mean_deviation(typical_price, sma)
            
            # Avoid division by zero
            mean_deviation = mean_deviation.replace(0, float('nan'))
            
            cci = (typical_price - sma) / (self.constant * mean_deviation)
            
            # Replace infinite values with NaN
            cci = cci.replace([float('inf'), float('-inf')], float('nan'))
            
            return cci
            
        except Exception as e:
            print(f"Error calculating CCI: {str(e)}")
            return pd.Series(float('nan'), index=close.index)

    def apply_strategy(self, df):
        """
        Apply CCI strategy to the dataframe
        
        Parameters:
        df (pandas.DataFrame): DataFrame with OHLC data
        
        Returns:
        pandas.DataFrame: DataFrame with CCI values and signals
        """
        try:
            # Create a copy to avoid modifying original data
            df = df.copy()
            
            # Calculate CCI
            df['CCI'] = self.calculate_cci(df['Close'], df['High'], df['Low'])
            
            # Generate trading signals
            # Using fillna(False) to ensure no NaN values in signals
            df['BuySignal'] = (df['CCI'] < -100).fillna(False)
            df['SellSignal'] = (df['CCI'] > 100).fillna(False)
            
            return df
            
        except Exception as e:
            print(f"Error applying CCI strategy: {str(e)}")
            return df