from binance.client import Client
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Binance API 設定
API_KEY = ''  # 你的 API Key
API_SECRET = ''  # 你的 Secret Key
client = Client(API_KEY, API_SECRET)

# 取得 BTC/USDT K 線數據
def get_binance_klines(symbol="BTCUSDT", interval=Client.KLINE_INTERVAL_1HOUR, limit=500):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume',
                                       'close_time', 'quote_asset_volume', 'number_of_trades',
                                       'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['close'] = df['close'].astype(float)  # 確保價格是 float
    df.set_index('timestamp', inplace=True)
    return df[['close']]  # 只保留收盤價

# 回測策略
def backtest(data, buy_levels, buy_multipliers, take_profit, stop_loss, leverage):
    initial_balance = 1000  # 初始資金
    balance = initial_balance
    position = 0
    entry_price = None
    trade_log = []
    buy_points = []  # 紀錄買入點
    sell_points = []  # 紀錄賣出點

    for i in range(1, len(data)):
        price = data["close"][i]

        # 檢查是否觸發買入點
        for level, qty_multiplier in zip(buy_levels, buy_multipliers):
            if entry_price is None or price <= entry_price * (1 + level / 100):
                buy_qty = (initial_balance / price) * qty_multiplier
                position += buy_qty
                entry_price = price
                trade_log.append(("BUY", data.index[i], price, buy_qty))
                buy_points.append((data.index[i], price))  # 記錄買入點
                break  # 只買一次，避免同時多個加倉

        # 檢查是否達到止盈
        if entry_price and price >= entry_price * (1 + take_profit / 100):
            profit = position * (price - entry_price) * leverage
            balance += profit
            position = 0  # 清空倉位
            trade_log.append(("SELL", data.index[i], price, profit))
            sell_points.append((data.index[i], price))  # 記錄賣出點

        # 檢查是否達到止損
        if balance <= initial_balance * (1 + stop_loss / 100):
            print("❌ 觸發止損！回測結束")
            break

    return trade_log, balance, buy_points, sell_points

# 畫圖顯示回測結果
def plot_backtest(data, buy_points, sell_points):
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data["close"], label="BTC/USDT Price", color="gray")

    # 標記買入點（🔵 藍色圓點）
    buy_times, buy_prices = zip(*buy_points) if buy_points else ([], [])
    plt.scatter(buy_times, buy_prices, color="blue", marker="o", label="Buy Points")

    # 標記賣出點（🔴 紅色圓點）
    sell_times, sell_prices = zip(*sell_points) if sell_points else ([], [])
    plt.scatter(sell_times, sell_prices, color="red", marker="o", label="Sell Points")

    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title("BTC/USDT 回測結果")
    plt.legend()
    plt.show()

# 主程式執行
if __name__ == "__main__":
    print("📡 正在從 Binance 下載 BTC/USDT K 線數據...")
    data = get_binance_klines()

    # 設定回測參數
    buy_levels = [-7, -14, -21, -28, -35, -42, -49]  # 買入點（%）
    buy_multipliers = [1, 2, 4, 8, 16, 32, 64]  # 對應的加倉倍數
    take_profit = 5  # 止盈（%）
    stop_loss = -30  # 最大總虧損（%）
    leverage = 3  # 槓桿倍率

    print("🚀 開始回測...")
    trades, final_balance, buy_points, sell_points = backtest(data, buy_levels, buy_multipliers, take_profit, stop_loss, leverage)

    print(f"✅ 回測完成，最終資金：{final_balance}")
    for trade in trades:
        print(trade)

    print("📊 顯示視覺化結果...")
    plot_backtest(data, buy_points, sell_points)
