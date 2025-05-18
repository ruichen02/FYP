import numpy as np

class OBVStrategy:
    def __init__(self):
        pass

    def calculate_obv(self, close, volume):
        """Calculate the On-Balance Volume (OBV) indicator."""
        obv = [0]  # Start with 0 as initial OBV
        for i in range(1, len(close)):
            if close[i] > close[i - 1]:
                obv.append(obv[-1] + volume[i])  # Positive volume if price rises
            elif close[i] < close[i - 1]:
                obv.append(obv[-1] - volume[i])  # Negative volume if price falls
            else:
                obv.append(obv[-1])  # No change if prices are the same
        return np.array(obv)

    def apply_strategy(self, df):
        # Check if the necessary columns exist
        if 'Close' not in df.columns or 'Volume' not in df.columns:
            raise ValueError("DataFrame must contain 'Close' and 'Volume' columns")
        
        # Calculate OBV and add it to the DataFrame
        df['OBV'] = self.calculate_obv(df['Close'], df['Volume'])
    
        # Logic-based Buy and Sell Signals
        df['BuySignal'] = df['OBV'] > df['OBV'].shift(1)  # Buy when OBV increases
        df['SellSignal'] = df['OBV'] < df['OBV'].shift(1)  # Sell when OBV decreases
    
        # Ensure BuySignal and SellSignal columns exist
        if 'BuySignal' not in df.columns or 'SellSignal' not in df.columns:
            raise ValueError("OBV strategy signals not found in the DataFrame")
        
        return df