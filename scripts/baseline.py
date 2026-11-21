"""Naive forecast baselines for weekly stocker auction prices.

Uses the same data and split as the SARIMAX result reported in the README:
the Feb-2025 dataset archived in old_data/aggregated_data.csv, CPI-adjusted
to the last week's dollars, with a sequential 90/10 train/test split.

Run from the repository root or the scripts folder:
    python scripts/baseline.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parent.parent / "old_data" / "aggregated_data.csv"
TRAIN_FRACTION = 0.9


def load_series(path=DATA):
    df = pd.read_csv(path)
    base_cpi = df["CPI_US"].iloc[-1]
    df["AVG_PRICE_AUCTION"] = df["AVG_PRICE_AUCTION"] * (base_cpi / df["CPI_US"])
    df["DATE"] = pd.to_datetime(df["DATE"])
    return df.sort_values("DATE").set_index("DATE")["AVG_PRICE_AUCTION"].dropna()


def metrics(actual, predicted):
    actual, predicted = np.asarray(actual), np.asarray(predicted)
    err = actual - predicted
    return {
        "MAE": np.mean(np.abs(err)),
        "RMSE": np.sqrt(np.mean(err**2)),
        "MAPE (%)": np.mean(np.abs(err / actual)) * 100,
        "R2": 1 - np.sum(err**2) / np.sum((actual - actual.mean()) ** 2),
    }


def main():
    y = load_series()
    n_train = int(len(y) * TRAIN_FRACTION)
    train, test = y.iloc[:n_train], y.iloc[n_train:]
    steps = np.arange(1, len(test) + 1)
    slope = (train.iloc[-1] - train.iloc[0]) / (len(train) - 1)

    # Both baselines forecast the whole test period from the end of training,
    # the same multi-step setup as the SARIMAX forecast.
    forecasts = {
        "Naive (last value)": np.repeat(train.iloc[-1], len(test)),
        "Drift": train.iloc[-1] + slope * steps,
    }

    print(f"{len(y)} weeks ({y.index.min().date()} to {y.index.max().date()}); "
          f"test = last {len(test)} weeks from {test.index.min().date()}")
    rows = {name: metrics(test, f) for name, f in forecasts.items()}
    print(pd.DataFrame(rows).T.round(2).to_string())


if __name__ == "__main__":
    main()
