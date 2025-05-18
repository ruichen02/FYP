import numpy as np

class ADXStrategy:
    def __init__(self, length=14, threshold=20):
        # Validate and convert length to integer
        self.length = int(length) if length > 0 else 14  # Default to 14 if invalid
        self.threshold = float(threshold)

    def true_range(self, df):
        # Calculate True Range
        return np.maximum(np.maximum(df['High'] - df['Low'], 
                                     np.abs(df['High'] - df['Close'].shift(1))),
                          np.abs(df['Low'] - df['Close'].shift(1)))

    def directional_movement(self, df):
        # Calculate Directional Movements
        df['DirectionalMovementPlus'] = np.where(df['High'] - df['High'].shift(1) > df['Low'].shift(1) - df['Low'], 
                                                 np.maximum(df['High'] - df['High'].shift(1), 0), 0)
        df['DirectionalMovementMinus'] = np.where(df['Low'].shift(1) - df['Low'] > df['High'] - df['High'].shift(1),
                                                  np.maximum(df['Low'].shift(1) - df['Low'], 0), 0)
        return df

    def smoothed_values(self, df, length):
        # Smooth True Range and Directional Movements
        df['SmoothedTrueRange'] = df['TrueRange'].rolling(window=length).mean()
        df['SmoothedDirectionalMovementPlus'] = df['DirectionalMovementPlus'].rolling(window=length).mean()
        df['SmoothedDirectionalMovementMinus'] = df['DirectionalMovementMinus'].rolling(window=length).mean()
        return df

    def calculate_adx(self, df):
        # Calculate DX and ADX
        df['DX'] = np.abs(df['SmoothedDirectionalMovementPlus'] - df['SmoothedDirectionalMovementMinus']) / (
                    df['SmoothedDirectionalMovementPlus'] + df['SmoothedDirectionalMovementMinus']) * 100
        df['ADX'] = df['DX'].rolling(window=self.length).mean()
        return df

    def apply_strategy(self, df):
        """
        Apply ADX strategy to the dataframe
        
        Parameters:
        df (pandas.DataFrame): DataFrame with OHLC data
        
        Returns:
        pandas.DataFrame: DataFrame with ADX and signals
        """
        # Create a copy to avoid modifying the original data
        df = df.copy()

        # Calculate True Range, Directional Movements, and ADX
        df['TrueRange'] = self.true_range(df)
        df = self.directional_movement(df)
        df = self.smoothed_values(df, self.length)
        df = self.calculate_adx(df)

        # Add ADX to the dataframe
        df['ADX'] = df['ADX']

        # Generate Buy and Sell signals based on ADX threshold
        df['BuySignal'] = (df['ADX'] > self.threshold) & (df['Close'] > df['Close'].shift(1))
        df['SellSignal'] = (df['ADX'] > self.threshold) & (df['Close'] < df['Close'].shift(1))

        return df