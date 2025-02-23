# 前置作業
## 使用 venv 創建此專案才需要的套件
`python -m venv venv`

# 啟用該環境
`venv\Scripts\activate`

如果 myenv 有被列入版控，執行以下
```git=
git rm -r cached .
git add .
git commit -m "Fix gitignore"
```

# 安裝套件
pip install pandas numpy matplotlib ccxt python-binance