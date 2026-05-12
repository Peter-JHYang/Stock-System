import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

from src.ta_indicators import sma, rsi
from src.fund_fetcher import fetch_three_institutions
from src.backtester import SimpleBacktester
from src.alerting import send_webhook_alert


st.set_page_config(page_title="台灣股市分析（範例）", layout="wide")
st.title("台灣股市分析 — 範例")

# --- 價格範例 ---
sample_path = Path(__file__).resolve().parents[1] / "data" / "sample.csv"
if sample_path.exists():
    df = pd.read_csv(sample_path)
else:
    df = pd.DataFrame({"close": [10, 10.5, 10.2, 11, 10.8, 11.5, 12, 11.8]})

st.subheader("價格範例")
st.write("最近價格：", df["close"].tail().tolist())
window = st.slider("SMA 週期", min_value=2, max_value=50, value=5)
st.line_chart(sma(df["close"], window).rename(f"SMA{window}"))
st.subheader("RSI (14)")
st.line_chart(rsi(df["close"], 14).rename("RSI14"))


# --- 三大法人（籌碼）顯示 ---
st.header("三大法人 / 籌碼")
col1, col2 = st.columns(2)
with col1:
    sel_date = st.date_input("選擇日期", value=date.today())
    date_str = sel_date.strftime("%Y%m%d")
    st.write("查詢日期：", date_str)

with col2:
    st.write("說明：呼叫 TWSE 法人資料 API 並顯示結果（範例）")

with st.spinner("抓取三大法人資料..."):
    fund_df = fetch_three_institutions(date_str)

if fund_df is None or fund_df.empty:
    st.info("目前沒有可顯示的法人資料（範例或 API 需回應）")
else:
    st.subheader("法人資料表格")
    st.dataframe(fund_df.head(200))

    # 嘗試找出外資或主要欄位並畫圖（若存在）
    plot_cols = [c for c in fund_df.columns if "foreign" in c.lower() or "外資" in c]
    if len(plot_cols) == 0:
        for cand in ["外資買賣超股數", "Foreign", "foreign_net"]:
            if cand in fund_df.columns:
                plot_cols = [cand]
                break

    if plot_cols:
        st.subheader("外資買賣超（示意）")
        try:
            agg = fund_df.groupby("stock")[plot_cols[0]].sum().sort_values(ascending=False).head(20)
            st.bar_chart(agg)
        except Exception:
            st.line_chart(fund_df[plot_cols[0]].astype(float))


# --- 回測與警示 ---
st.header("回測與警示")
with st.sidebar.expander("回測參數", expanded=True):
    short = st.number_input("短期 SMA", min_value=1, max_value=200, value=5)
    long = st.number_input("長期 SMA", min_value=1, max_value=400, value=20)
    initial_cash = st.number_input("初始資金", min_value=100.0, value=100000.0)
    tc = st.number_input("交易成本比例", min_value=0.0, max_value=0.1, value=0.001, format="%.4f")
    max_pos = st.number_input("最大投入比例", min_value=0.0, max_value=1.0, value=1.0, format="%.2f")
    dd_alert_threshold = st.number_input("回撤警示門檻 (負數, 例如 -0.2)", value=-0.2, format="%.2f")
    webhook_url = st.text_input("Webhook URL (選填，用於警示)")

if st.button("執行回測"):
    bt = SimpleBacktester(df)
    equity_df, metrics = bt.run_sma_strategy(short=int(short), long=int(long), initial_cash=float(initial_cash),
                                             transaction_cost=float(tc), max_position_fraction=float(max_pos))

    st.subheader("回測績效")
    st.metric("總報酬", f"{metrics['total_return']*100:.2f}%")
    st.metric("年化報酬", f"{metrics['annualized_return']*100:.2f}%")
    st.metric("最大回撤", f"{metrics['max_drawdown']*100:.2f}%")

    st.subheader("權益曲線")
    st.line_chart(equity_df['equity'])

    # 若超過回撤門檻，嘗試送出 webhook 警示
    try:
        if metrics.get('max_drawdown') is not None and metrics['max_drawdown'] <= float(dd_alert_threshold):
            if webhook_url:
                payload = {"type": "backtest_alert", "metric": metrics}
                ok = send_webhook_alert(webhook_url, payload)
                if ok:
                    st.success("已傳送警示到 Webhook")
                else:
                    st.error("嘗試傳送 Webhook 但失敗")
            else:
                st.warning("達到回撤門檻，但未設定 Webhook URL")
    except Exception as e:
        st.error(f"警示處理時發生錯誤：{e}")
