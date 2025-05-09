import pandas as pd
import numpy as np

def print_all():
    print(stocker_data.head())
    print(corn_futures.head())
    print(cpi_data.head())
    print(diesel_prices.head())
    print(cattle_futures.head())
    print(us_mxn_rates.head())

# CONVERT EACH CSV INTO TIME-SERIES DATAFRAME
try:
    stocker_data = pd.read_csv(r'features_data\stocker_data.csv')
    stocker_data['DATE'] = pd.to_datetime(stocker_data['DATE'])
    stocker_data = stocker_data.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\stocker_data.csv')

try:
    corn_futures = pd.read_csv(r'features_data\corn_futures.csv')
    corn_futures['DATE'] = pd.to_datetime(corn_futures['DATE'])
    corn_futures = corn_futures.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\corn_futures.csv')

try:
    cpi_data = pd.read_csv(r'features_data\cpi_data.csv')
    cpi_data['DATE'] = pd.to_datetime(cpi_data['DATE'])
    cpi_data = cpi_data.sort_values('DATE', ignore_index=True).set_index('DATE')

    # print(df_cpi_data)
except:
    print(r'features_data\cpi_data.csv')

try:
    diesel_prices = pd.read_csv(r'features_data\diesel_prices.csv')
    diesel_prices['DATE'] = pd.to_datetime(diesel_prices['DATE'])
    diesel_prices = diesel_prices.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\diesel_prices.csv')

try:
    cattle_futures = pd.read_csv(r'features_data\feeder_cattle_futures.csv')
    cattle_futures['DATE'] = pd.to_datetime(cattle_futures['DATE'])
    cattle_futures = cattle_futures.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\feeder_cattle_futures.csv')

try:
    us_mxn_rates = pd.read_csv(r'features_data\us_mxn_exchange_rates.csv')
    us_mxn_rates['DATE'] = pd.to_datetime(us_mxn_rates['DATE'])
    us_mxn_rates = us_mxn_rates.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\us_mxn_exchange_rates.csv')

try:
    federal_interest_rates = pd.read_csv(r'features_data\federal_interest_rates.csv')
    federal_interest_rates['DATE'] = pd.to_datetime(federal_interest_rates['DATE'])
    federal_interest_rates = federal_interest_rates.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print()
    print(r'features_data\federal_interest_rates.csv')

try:
    alfafa_hay_ppi = pd.read_csv(r'features_data\alfafa_hay_ppi.csv')
    alfafa_hay_ppi['DATE'] = pd.to_datetime(alfafa_hay_ppi['DATE'])
    alfafa_hay_ppi = alfafa_hay_ppi.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\alfafa_hay_ppi.csv')

try:
    corn_ppi = pd.read_csv(r'features_data\corn_ppi.csv')
    corn_ppi['DATE'] = pd.to_datetime(corn_ppi['DATE'])
    corn_ppi = corn_ppi.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\corn_ppi.csv')

# print_all()

# RESAMPLE DAILY AND MONTHLY DATA TO WEEKLY
corn_futures = corn_futures.resample('W-FRI').mean()
cattle_futures = cattle_futures.resample('W-FRI').mean()
us_mxn_rates = us_mxn_rates.resample('W-FRI').mean()
cpi_data = cpi_data.resample('W-FRI').ffill()
diesel_prices = diesel_prices.resample('W-FRI').ffill()
federal_interest_rates = federal_interest_rates.resample('W-FRI').ffill()
alfafa_hay_ppi = alfafa_hay_ppi.resample('W-FRI').ffill()
corn_ppi = corn_ppi.resample('W-FRI').ffill()

# print(df_diesel_prices.to_string)
# print(df_corn_futures.head())
# print(df_cattle_futures.head())
# print(df_us_mxn_rates.to_string())

# df_diesel_prices['DATE'] = df_diesel_prices['DATE'] + pd.DateOffset(days=-3)

# ENSURE MASTER INDEX IS INDEXED WEEKLY ON FRIDAY
stocker_data.index = stocker_data.index.where(
    stocker_data.index.dayofweek != 5,
    stocker_data.index - pd.Timedelta(days=1)
)
master_index = stocker_data.index
# print(master_index)

# print(cpi_data.head())

# ALIGN ALL DATAFRAMES ON COMMON WEEKLY INDEX
corn_futures = corn_futures.reindex(master_index).ffill()
cattle_futures = cattle_futures.reindex(master_index).ffill()
us_mxn_rates = us_mxn_rates.reindex(master_index).ffill()
cpi_data = cpi_data.reindex(master_index).ffill()
diesel_prices = diesel_prices.reindex(master_index).ffill()
federal_interest_rates = federal_interest_rates.reindex(master_index).ffill()
alfafa_hay_ppi = alfafa_hay_ppi.reindex(master_index).ffill()
corn_ppi = corn_ppi.reindex(master_index).ffill()


# print(cpi_data.head())

# print_all()

# MERGE THE DATAFRAMES TOGETHER
aggregated_df = pd.concat([stocker_data, corn_futures, cattle_futures, us_mxn_rates, cpi_data, diesel_prices, federal_interest_rates, alfafa_hay_ppi, corn_ppi], axis=1)

# DATA PREPROCESSING
aggregated_df.replace("#DIV/0!", np.nan, inplace=True)
aggregated_df.infer_objects(copy=False)
aggregated_df['AVG_PRICE_AUCTION'] = pd.to_numeric(aggregated_df['AVG_PRICE_AUCTION'], errors='coerce')
aggregated_df = aggregated_df.interpolate(method='linear')
aggregated_df.to_csv('aggregated_data.csv')