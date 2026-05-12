# 台灣股市分析系統 (範例專案)

快速開始：

```bash
cd tw_stock_project
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
streamlit run src/app.py
```

此專案包含：

使用範例
 - 取得三大法人資料：在 Python 中匯入 `src.fund_fetcher.fetch_three_institutions(date)`
 - 執行回測：匯入 `src.backtester.SimpleBacktester`，並呼叫 `run_sma_strategy()`
 - 傳送警示：`src.alerting.send_webhook_alert(url,payload)` 或 `send_smtp_alert(cfg, subj, body)`

MOPS 財報抓取（範例）

```python
from src.mops_fetcher import fetch_mops_financials

# 範例：取得 2025 年第 2 季的財報摘要
df = fetch_mops_financials("2330", 2025, 2)
print(df.to_dict(orient="records"))
```

回傳欄位說明（範例）：
- `eps`: 每股盈餘（若解析到）
- `revenue`: 營業收入 / 營收（若解析到）
- `net_income`: 稅後淨利 / 本期淨利（若解析到）
- `raw_html`: 找到的表格 HTML 原始字串，便於後續自訂解析

注意：MOPS 頁面結構與參數可能改變，此為可擴充的解析骨架，實務使用時請依官方文件與實際 HTML 調整關鍵字與欄位解析邏輯。

## 安裝與常見問題

快速安裝（推薦）:

```bash
cd ~/tw_stock_project
./install.sh
```

或手動：

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
```

啟動本地 Streamlit UI：

```bash
. .venv/bin/activate
streamlit run src/app.py
```

若你在執行 `streamlit run src/app.py` 時遇到 `No module named 'src'`，請確定你在專案根目錄並且已執行 `pip install -e .`，或用 `PYTHONPATH=. streamlit run src/app.py` 啟動。

macOS 常見問題：
- 若遇到 BeautifulSoup 相關的 lxml 解析器問題，請先安裝系統套件：

```bash
brew install libxml2 libxslt
export LDFLAGS="-L/usr/local/opt/libxml2/lib -L/usr/local/opt/libxslt/lib"
export CPPFLAGS="-I/usr/local/opt/libxml2/include -I/usr/local/opt/libxslt/include"
```

- 若遇到需要編譯的套件建議先安裝 Xcode command line tools：

```bash
xcode-select --install
```

CI: 本專案已包含 GitHub Actions 工作流程，在 push/PR 到 `main` 時會執行 `pytest`。

