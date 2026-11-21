# Forecasting Texas Stocker Cattle Prices

Aggie Research Program project (Spring–Summer 2025) by Jonathan Liu, mentored by Vishnudas Kulangara-Veettil and Dr. Karun Kaniyamattam (Texas A&M Department of Animal Science). It continues the [Fall 2024 stocker profitability project](https://github.com/JBL168/beef_value_chain_project_fall_2024).

The goal is to forecast the weekly average price of stocker cattle at Texas auctions from futures prices, input costs, and macroeconomic indicators.

## Data

| Series | Source | Frequency |
|---|---|---|
| Texas auction prices and receipts (target) | USDA AMS MyMarketNews, National Feeder & Stocker Cattle Summary (`SJ_LS850`) | Weekly |
| Feeder cattle futures, corn futures | Business Insider market data | Daily |
| USD/MXN exchange rate | Investing.com | Daily |
| U.S. CPI (`CPIAUCNS`), federal funds rate (`FEDFUNDS`) | FRED | Monthly |
| Diesel retail price | U.S. Energy Information Administration | Weekly |
| Alfalfa hay PPI, corn PPI | U.S. Bureau of Labor Statistics | Monthly |

The target, `AVG_PRICE_AUCTION`, is the average Texas auction price ($/cwt) across Medium & Large 1 and 1–2 steers and heifers.

The modeling results below use the dataset archived in `old_data/aggregated_data.csv`: 369 weeks from Nov 2017 to Feb 2025. `aggregated_data.csv` in the root has since been refreshed through Sep 2025, so the saved notebook outputs will not reproduce exactly against it.

## Pipeline

| Step | Script | Output |
|---|---|---|
| 1. Download weekly reports | `scripts/scraper.py` | `National_Feeder_Stocker_Cattle_Summary/` (not committed) |
| 2. Parse reports | `scripts/parse_usda_files.py` | `data/stocker_data.csv` |
| 3. Align and merge features | `scripts/data_aggregation.py` | `aggregated_data.csv` |
| 4. Engineer and select features | `scripts/feature_selection.py` | `model_features.csv` |
| 5. Naive baselines | `scripts/baseline.py` | printed metrics |

**Scraping and parsing.** `scraper.py` uses requests and BeautifulSoup to page through the MyMarketNews report archive and download each weekly text report. `parse_usda_files.py` uses regular expressions to pull the week-ending date, national and Texas auction receipts, and the Texas steer and heifer price sections from each report.

**Alignment.** Daily series are averaged to weeks ending Friday, and monthly series are forward-filled, so every feature lines up with the weekly auction report. Prices are inflation-adjusted to the last week's dollars using CPI.

**Features.** The September 2025 refresh added lagged corn-to-feeder and diesel-to-feeder price ratios, monthly CPI change, and the federal funds rate.

## Models

Notebooks in `old_notebooks/`, trained on the first 90% of weeks and tested on the remaining 37 weeks (May 2024 – Feb 2025):

- **SARIMAX** (`sarimax.ipynb`): order (0,1,1)(1,0,0)₁₂, selected by `pmdarima.auto_arima` (AIC) on the price series, then refit with corn futures, diesel, and feeder cattle futures as exogenous regressors. Includes residual diagnostics (Shapiro–Wilk, Jarque–Bera, Ljung–Box, Durbin–Watson).
- **Linear regression** (`linear_regression.ipynb`) on the same-week features.
- **LSTM** (`lstm.ipynb`, PyTorch): 16-week input window, 8-week output, trained for 3,000 epochs and tested on the final 8-week window.
- **ARIMA** (`arima.ipynb`) on the price series alone.

## Results (Feb-2025 dataset)

| Model | Test period | MAE ($/cwt) | RMSE | MAPE | R² |
|---|---|---|---|---|---|
| **SARIMAX** | 37 weeks | **10.06** | **13.30** | **3.66%** | **0.11** |
| Drift baseline | 37 weeks | 11.17 | 14.34 | 4.09% | 0.00 |
| Naive baseline (last value) | 37 weeks | 12.67 | 16.72 | 4.60% | −0.36 |
| Linear regression | 37 weeks | 13.40 | 16.70 | – | −0.36 |
| LSTM | 8 weeks | 20.48 | 21.94 | – | −13.60 |

Baselines come from `scripts/baseline.py`; model rows come from the saved notebook outputs. The LSTM fit its training data closely (R² 0.96) but failed on the test window, a clear sign of overfitting.

### Limitations

- **SARIMAX uses realized exogenous values.** The forecast is given the actual futures and diesel prices during the test period, so it is a conditional forecast, not one that could be made in advance.
- **Weak improvement over baselines.** SARIMAX beats the naive and drift forecasts, but its R² of 0.11 shows it explains little of the week-to-week variation. Ljung–Box rejects white-noise residuals (p < 0.001), so autocorrelation remains.
- **Seasonal period.** The seasonal term uses a period of 12 on weekly data; an annual cycle would be 52.
- **Single holdout.** Each model is scored on one train/test split, not a rolling-origin backtest.
- **ARIMA result not reported.** `inverse_difference` in `arima.ipynb` rebuilds the forecast from the first training value instead of the last, which shifts every prediction by a constant (all residuals have the same sign, mean 61.5). The notebook's metrics reflect that offset, not the model.

## Setup

Requires Python with pandas, numpy, scikit-learn, statsmodels, pmdarima, PyTorch, BeautifulSoup, and matplotlib/seaborn.

The scraper uses the public MyMarketNews report archive and needs no API key.

```bash
python scripts/scraper.py
python scripts/parse_usda_files.py
python scripts/data_aggregation.py
python scripts/feature_selection.py
python scripts/baseline.py
```

## Repository layout

```
scripts/            Scraping, parsing, aggregation, feature selection, baselines
old_notebooks/      Modeling notebooks behind the reported results
notebooks/          Later ARIMA experiments on the refreshed data
data/               Feature source files (data/originals/ holds raw downloads)
old_data/           Feb-2025 dataset used for the reported results
figures/            Model and data plots
```
