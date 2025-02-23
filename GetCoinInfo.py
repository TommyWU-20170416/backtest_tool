from binance.client import Client
import pandas as pd
# 初始化客戶端
client = Client('', '') 
# 獲取 BTCUSDT 的現貨 K 線數據
klines = client.get_klines(symbol='BTCUSDT', interval=Client.KLINE_INTERVAL_1HOUR, limit=100)
# 將數據轉換為 DataFrame
df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume', 'number_of_trades', 'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
# 轉換時間戳
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
# 打印前幾行數據
print(df.head())