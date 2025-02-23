from binance.client import Client
import pandas as pd

# Binance API 設定
API_KEY = ''  # 你的 API Key
API_SECRET = ''
client = Client(API_KEY, API_SECRET)

# 下載近 3 個月 K 線數據
def fetch_binance_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1HOUR, days=90, filename="btcusdt_3months.csv"):
    print("📡 正在下載 Binance K 線數據...")
    
    # 下載數據
    klines = client.get_klines(symbol=symbol, interval=interval, limit=1000)
    
    # 轉換為 DataFrame
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                       'close_time', 'quote_asset_volume', 'number_of_trades',
                                       'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['close'] = df['close'].astype(float)
    df.set_index('timestamp', inplace=True)

    # 存成 CSV
    df.to_csv(filename)
    print(f"✅ 數據已儲存到 {filename}")

# 執行下載
fetch_binance_klines()
