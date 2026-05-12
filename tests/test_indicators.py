import pandas as pd
from src.ta_indicators import sma, rsi


def test_sma_basic():
    s = pd.Series([1, 2, 3, 4, 5])
    out = sma(s, 3)
    assert len(out) == 5
    assert out.iloc[-1] == (3 + 4 + 5) / 3


def test_rsi_basic():
    s = pd.Series([1, 2, 1, 2, 3, 2, 3, 4])
    out = rsi(s, 3)
    assert len(out) == len(s)
    assert out.isna().sum() == 0
