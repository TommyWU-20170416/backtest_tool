# 使用 venv 創建此專案才需要的套件
python -m venv myenv

# 啟用該環境
myenv\Scripts\activate
如果 myenv 有被列入版控，執行以下
git rm -r cached .
git add .
git commit -m "Fix gitignore"

# 安裝套件
pip install python-binance pandas