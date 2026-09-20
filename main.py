import os
import time
import ccxt
import pandas as pd
import strategy

# Read secure API Keys from Render Environment Variables
API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

SYMBOL = "BTC/USDT"
TIMEFRAME = "1m"      # 1-minute chart for testing

def init_exchange():
    exchange = ccxt.binance({
        'apiKey': API_KEY,
        'secret': API_SECRET,
        'enableRateLimit': True,
        'options': {
            'defaultType': 'future'  # Set to 'spot' if using Spot keys
        }
    })
    # Set sandbox to False since you are using live read-only keys
    exchange.set_sandbox_mode(False)
    return exchange

def run_bot():
    print("==========================================")
    print(" 24/7 CLOUD MONITOR (BINANCE LIVE READ-ONLY) ")
    print("==========================================")

    exchange = init_exchange()

    while True:
        try:
            # 1. Fetch live market candles from Binance
            bars = exchange.fetch_ohlcv(SYMBOL, timeframe=TIMEFRAME, limit=50)
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # 2. Run pattern detection
            df = strategy.find_pivots(df, window=2)

            latest_bar = df.iloc[-2]  # Last closed candle
            current_price = df['close'].iloc[-1]

            print(f"[{pd.Timestamp.now()}] {SYMBOL} Price: ${current_price:,.2f} | Pivot High: {latest_bar['pivot_high']} | Pivot Low: {latest_bar['pivot_low']}")

            # 3. Log pattern alerts (Read-only keys safely monitor without executing orders)
            if latest_bar['pivot_low']:
                print("🔥 [PAPER SIGNAL] PIVOT LOW DETECTED!")
            elif latest_bar['pivot_high']:
                print("⚡ [PAPER SIGNAL] PIVOT HIGH DETECTED!")

            # Wait 60 seconds before checking next candle
            time.sleep(60)

        except Exception as e:
            print("⚠️ Cloud Loop Error:", str(e))
            time.sleep(15)

if __name__ == "__main__":
    run_bot()
