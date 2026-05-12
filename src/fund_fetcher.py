import requests
import pandas as pd


def fetch_three_institutions(date: str) -> pd.DataFrame:
    """呼叫 TWSE 的三大法人資料 API（範例）。

    參數 date 格式為 YYYYMMDD。
    回傳 DataFrame；若失敗則回傳空 DataFrame。
    """
    url = "https://www.twse.com.tw/fund/T86"
    params = {"response": "json", "date": date, "selectType": "ALL"}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        js = r.json()
    except Exception:
        return pd.DataFrame()

    data = js.get("data", [])
    fields = js.get("fields", [])
    if not data or not fields:
        return pd.DataFrame()

    df = pd.DataFrame(data, columns=fields)
    df.insert(0, "date", date)
    # 嘗試把數字欄位轉為 float
    for col in df.columns:
        try:
            df[col] = df[col].astype(str).str.replace(",", "", regex=False).str.replace("-", "0").astype(float)
        except Exception:
            pass

    return df
