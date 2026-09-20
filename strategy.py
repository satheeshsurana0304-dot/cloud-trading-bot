import pandas as pd

def find_pivots(df, window=2):
    """Identifies Pivot Highs (Peaks) and Pivot Lows (Valleys)."""
    df['pivot_high'] = False
    df['pivot_low'] = False

    for i in range(window, len(df) - window):
        # Pivot High Logic (Peak)
        if all(df['high'].iloc[i] > df['high'].iloc[i - j] for j in range(1, window + 1)) and \
           all(df['high'].iloc[i] > df['high'].iloc[i + j] for j in range(1, window + 1)):
            df.loc[df.index[i], 'pivot_high'] = True

        # Pivot Low Logic (Valley)
        if all(df['low'].iloc[i] < df['low'].iloc[i - j] for j in range(1, window + 1)) and \
           all(df['low'].iloc[i] < df['low'].iloc[i + j] for j in range(1, window + 1)):
            df.loc[df.index[i], 'pivot_low'] = True

    return df
