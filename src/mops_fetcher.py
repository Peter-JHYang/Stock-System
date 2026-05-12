import requests
import pandas as pd
from bs4 import BeautifulSoup
from typing import Optional


def _parse_number(s: str) -> Optional[float]:
    if s is None:
        return None
    t = str(s).strip()
    if t in ("", "-", "—", "nan"):
        return None
    # 移除千分位逗號與括號（括號表示負數）
    neg = False
    if t.startswith("(") and t.endswith(")"):
        neg = True
        t = t[1:-1]
    t = t.replace(",", "").replace("%", "")
    try:
        v = float(t)
        if neg:
            v = -v
        return v
    except Exception:
        return None


def fetch_mops_financials(stock_id: str, year: int, season: int) -> pd.DataFrame:
    """抓取並解析 MOPS 財報（嘗試抽取 EPS、營收、稅後淨利等欄位）。

    參數:
      - stock_id: 證券代碼（字串）
      - year: 西元年（例如 2025）
      - season: 第幾季（1-4）

    回傳: DataFrame，若成功會包含欄位 `eps`, `revenue`, `net_income`，以及 `raw_html`（找到的表格 HTML 字串）。
    注意: MOPS 網頁格式會變，這是一個可擴充的解析骨架。
    """
    # 範例查詢 URL（視實際 MOPS 路徑調整）
    url = "https://mops.twse.com.tw/mops/web/t163sb13"
    params = {"step": 1, "firstin": 1, "co_id": stock_id, "year": year - 1911, "season": season}

    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
    except Exception:
        return pd.DataFrame()

    tables = soup.find_all("table")
    if not tables:
        return pd.DataFrame()

    # 關鍵字對應：嘗試找尋每股盈餘、營收、淨利等
    keys_map = {
        "eps": ["每股盈餘", "EPS"],
        "revenue": ["營業收入", "營收", "營業收入淨額"],
        "net_income": ["稅後淨利", "淨利", "本期淨利"],
    }

    result = {"eps": None, "revenue": None, "net_income": None, "raw_html": ""}

    for tbl in tables:
        # 儲存第一個表格 HTML 作為 raw
        if not result["raw_html"]:
            result["raw_html"] = str(tbl)

        # 以 row-wise 掃描，每列的文字合併，再找關鍵字
        for tr in tbl.find_all("tr"):
            texts = [td.get_text(separator=" ", strip=True) for td in tr.find_all(["td", "th"])]
            row_text = " ".join(texts)
            if not row_text:
                continue

            for k, kws in keys_map.items():
                if result.get(k) is not None:
                    continue
                for kw in kws:
                    if kw in row_text:
                        # 嘗試把該列中可能的數字取出
                        for tok in texts[::-1]:
                            val = _parse_number(tok)
                            if val is not None:
                                result[k] = val
                                break
                        if result.get(k) is not None:
                            break
                # 找到就跳出下一 key

    # 將結果包成 DataFrame
    df = pd.DataFrame([result])
    return df

