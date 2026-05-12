import pandas as pd
import numpy as np
from typing import Tuple, Dict


class SimpleBacktester:
    """簡單回測器：支援交易成本、最大持倉比例與績效指標計算。"""

    def __init__(self, price_df: pd.DataFrame, price_col: str = "close"):
        self.df = price_df.copy().reset_index(drop=True)
        if price_col not in self.df.columns:
            raise ValueError("price_col not in dataframe")
        self.price_col = price_col

    def _compute_metrics(self, equity_series: pd.Series, periods_per_year: int = 252) -> Dict:
        returns = equity_series.pct_change().fillna(0)
        total_return = equity_series.iloc[-1] / equity_series.iloc[0] - 1.0
        # 年化報酬（簡單估算）
        n_periods = len(equity_series)
        if n_periods > 1:
            annualized_return = (1 + total_return) ** (periods_per_year / n_periods) - 1
        else:
            annualized_return = 0.0

        sr = None
        if returns.std() > 0:
            sr = (returns.mean() / returns.std()) * np.sqrt(periods_per_year)

        # 最大回撤
        roll_max = equity_series.cummax()
        drawdown = (equity_series - roll_max) / roll_max
        max_dd = drawdown.min()

        return {
            "total_return": float(total_return),
            "annualized_return": float(annualized_return),
            "sharpe": float(sr) if sr is not None else None,
            "max_drawdown": float(max_dd),
        }

    def run_sma_strategy(self, short: int = 5, long: int = 20, initial_cash: float = 100000.0,
                         transaction_cost: float = 0.001, max_position_fraction: float = 1.0) -> Tuple[pd.DataFrame, Dict]:
        """執行 SMA 交叉策略。

        參數:
          - transaction_cost: 單次交易成本比例（例如 0.001 = 0.1%）
          - max_position_fraction: 最大可投入資金比例（0-1）

        回傳 (equity_df, metrics)
        """
        df = self.df.copy()
        df["sma_short"] = df[self.price_col].rolling(window=short, min_periods=1).mean()
        df["sma_long"] = df[self.price_col].rolling(window=long, min_periods=1).mean()
        df = df.dropna().reset_index(drop=True)

        position = 0  # 0 現金、1 多頭
        cash = float(initial_cash)
        shares = 0.0
        equity_curve = []

        for i, row in df.iterrows():
            price = float(row[self.price_col])
            # Buy signal
            if row["sma_short"] > row["sma_long"] and position == 0:
                invest_amount = cash * float(max_position_fraction)
                # 考慮買入時交易成本：買入價格視為 price*(1+tc)
                if price * (1 + transaction_cost) > 0:
                    shares = invest_amount / (price * (1 + transaction_cost))
                    cash = cash - invest_amount
                    position = 1
            # Sell signal
            elif row["sma_short"] < row["sma_long"] and position == 1:
                # 賣出時考慮交易成本：收到現金為 shares*price*(1-tc)
                proceeds = shares * price * (1 - transaction_cost)
                cash = cash + proceeds
                shares = 0.0
                position = 0

            total_value = cash + shares * price
            equity_curve.append({"index": i, "price": price, "equity": total_value, "position": position})

        equity_df = pd.DataFrame(equity_curve).set_index("index")
        metrics = self._compute_metrics(equity_df["equity"].astype(float))
        return equity_df, metrics

