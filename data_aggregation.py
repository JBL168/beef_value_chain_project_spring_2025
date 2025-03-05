import pandas as pd

# CONVERT EACH CSV INTO TIME-SERIES DATAFRAME
try:
    df_stocker_data = pd.read_csv(r'features_data\stocker_data.csv')
    df_stocker_data['DATE'] = pd.to_datetime(df_stocker_data['DATE'])
    df_stocker_data = df_stocker_data.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\stocker_data.csv')

try:
    df_corn_futures = pd.read_csv(r'features_data\corn_futures.csv')
    df_corn_futures['DATE'] = pd.to_datetime(df_corn_futures['DATE'])
    df_corn_futures = df_corn_futures.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\corn_futures.csv')

try:
    df_cpi_data = pd.read_csv(r'features_data\cpi_data.csv')
    df_cpi_data['DATE'] = pd.to_datetime(df_cpi_data['DATE'])
    df_cpi_data = df_cpi_data.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\cpi_data.csv')

try:
    df_diesel_prices = pd.read_csv(r'features_data\diesel_prices.csv')
    df_diesel_prices['DATE'] = pd.to_datetime(df_diesel_prices['DATE'])
    df_diesel_prices = df_diesel_prices.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\diesel_prices.csv')

try:
    df_cattle_futures = pd.read_csv(r'features_data\feeder_cattle_futures.csv')
    df_cattle_futures['DATE'] = pd.to_datetime(df_cattle_futures['DATE'])
    df_cattle_futures = df_cattle_futures.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\feeder_cattle_futures.csv')

try:
    df_us_mxn_rates = pd.read_csv(r'features_data\us_mxn_exchange_rates.csv')
    df_us_mxn_rates['DATE'] = pd.to_datetime(df_us_mxn_rates['DATE'])
    df_us_mxn_rates = df_us_mxn_rates.sort_values('DATE', ignore_index=True).set_index('DATE')
except:
    print(r'features_data\us_mxn_exchange_rates.csv')

print(df_stocker_data.head())
print(df_corn_futures.head())
print(df_cpi_data.head())
print(df_diesel_prices.head())
print(df_cattle_futures.head())
print(df_us_mxn_rates.head())
