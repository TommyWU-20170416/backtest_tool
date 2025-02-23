from binance.client import Client
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Binance API 設定
API_KEY = ''  # 你的 API Key
API_SECRET = ''  # 你的 Secret Key
client = Client(API_KEY, API_SECRET)

# 計算加權平均成本


def calculate_avg_entry_price(trades):
    total_cost = 0
    total_qty = 0
    for trade in trades:
        if trade[0] == "BUY":
            price, qty = trade[2], trade[3]
            total_cost += price * qty
            total_qty += qty
    return total_cost / total_qty if total_qty > 0 else None

# 取得 BTC/USDT K 線數據


def get_binance_klines_from_csv(file_path="csv/btcusdt_7days.csv"):
    df = pd.read_csv(file_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['close'] = df['close'].astype(float)
    df.set_index('timestamp', inplace=True)
    return df[['close']]

# 回測策略


def backtest(data, buy_levels, buy_multipliers, take_profit, stop_loss, leverage):
    initial_balance = 1000  # 初始資金
    balance = initial_balance
    position = 0
    entry_price = None
    trade_log = []
    buy_points = []  # 紀錄買入點
    sell_points = []  # 紀錄賣出點
    base_entry_price = None  # 初始買入價
    next_buy_level_index = 0  # 記錄下一次要檢查的買入層級索引

    for i in range(len(data)):
        price = data["close"][i]
        print(
            f"Price: {price}, Balance: {balance}, Position: {position}, Next Buy Level Index: {next_buy_level_index}")

        # 初始進場
        if base_entry_price is None:
            base_entry_price = price
            buy_qty = (initial_balance / price) * \
                buy_multipliers[0]  # 使用第一個加倉倍數
            position += buy_qty
            trade_log.append(("BUY", data.index[i], price, buy_qty))
            buy_points.append((data.index[i], price))
            entry_price = price  # 記錄初始進場價格
            next_buy_level_index = 1  # 下一次檢查的層級從第二層開始
            continue

        # 檢查是否觸發補倉
        if next_buy_level_index < len(buy_levels):
            level = buy_levels[next_buy_level_index]
            qty_multiplier = buy_multipliers[next_buy_level_index]
            if price <= base_entry_price * (1 + level / 100):
                buy_qty = (initial_balance / price) * qty_multiplier
                position += buy_qty
                trade_log.append(("BUY", data.index[i], price, buy_qty))
                buy_points.append((data.index[i], price))
                entry_price = price  # 更新 entry_price 為最新的買入價
                next_buy_level_index += 1  # 移動到下一個層級

        # 檢查是否達到止盈
        avg_entry_price = calculate_avg_entry_price(trade_log)
        if avg_entry_price and price >= avg_entry_price * (1 + take_profit / 100) and position > 0:
            profit = position * (price - avg_entry_price) * leverage
            balance += profit
            position = 0  # 清空倉位
            trade_log.append(("SELL", data.index[i], price, profit))
            sell_points.append((data.index[i], price))
            entry_price = None  # 清空 entry_price 以便下一次買入
            next_buy_level_index = 1  # 重置下一個買入層級索引

        # 檢查是否達到止損
        if balance <= initial_balance * (1 + stop_loss / 100):
            print("❌ 觸發止損！回測結束")
            break

    return trade_log, balance, buy_points, sell_points

# 畫圖顯示回測結果


def plot_backtest(data, buy_points, sell_points):
    plt.figure(figsize=(12, 6))
    plt.plot(data.index, data["close"], label="BTC/USDT Price", color="gray")

    # 標記買入點
    buy_times, buy_prices = zip(*buy_points) if buy_points else ([], [])
    plt.scatter(buy_times, buy_prices, color="blue",
                marker="o", label="Buy Points")

    # 標記賣出點
    sell_times, sell_prices = zip(*sell_points) if sell_points else ([], [])
    plt.scatter(sell_times, sell_prices, color="red",
                marker="o", label="Sell Points")

    plt.xlabel("Time")
    plt.ylabel("Price")
    plt.title("BTC/USDT 回測結果")
    plt.legend()
    plt.show()


# 主程式執行
if __name__ == "__main__":
    print("📡 從 csv 抓取 BTC/USDT K 線數據...")
    data = get_binance_klines_from_csv()

    # 設定回測參數
    buy_levels = [-1, -2, -3, -4, -5, -6, -7]  # 買入點（%）
    buy_multipliers = [1, 2, 4, 8, 16, 32, 64]  # 對應的加倉倍數
    take_profit = 2  # 止盈（%）
    stop_loss = -30  # 最大總虧損（%）
    leverage = 3  # 槓桿倍率

    print("🚀 開始回測...")
    trades, final_balance, buy_points, sell_points = backtest(
        data, buy_levels, buy_multipliers, take_profit, stop_loss, leverage)

    print(f"✅ 回測完成，最終資金：{final_balance}")
    for trade in trades:
        print(trade)

    print("📊 顯示視覺化結果...")
    plot_backtest(data, buy_points, sell_points)
