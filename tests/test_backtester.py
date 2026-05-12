import pandas as pd
from src.backtester import SimpleBacktester


def test_backtester_sma():
    prices = [10, 10.5, 11, 10.8, 11.5, 12, 11.8, 12.5, 13]
    df = pd.DataFrame({"close": prices})
    bt = SimpleBacktester(df)
    equity, metrics = bt.run_sma_strategy(short=2, long=3, initial_cash=1000)
    assert not equity.empty
    assert equity["equity"].iloc[-1] > 0
    # 檢查績效指標存在
    assert "total_return" in metrics and "max_drawdown" in metrics
