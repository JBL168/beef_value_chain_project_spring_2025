import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

df = pd.read_csv('aggregated_data.csv')
df['DATE'] = pd.to_datetime(df['DATE'])
df = df.sort_values('DATE', ignore_index=True).set_index('DATE').drop( # drop columns not used for training
    ['avg_price_steers_ML1', 
     'avg_price_steers_ML1_2', 
     'avg_price_heifers_ML1', 
     'avg_price_heifers_ML1_2', 
     'national_auctions', 
     'national_total', 
     'texas_auctions', 
     ], axis=1)

df['ΔCPI'] = df['CPI_US'].pct_change() * 100  # % change
df['ΔFED'] = df['FEDERAL_INTEREST_RATE']  # federal funds rate level (not differenced)
df['CORN_FEED_RATIO_L1'] = df['CORN_FUTURES_TYPICAL_PRICE'].shift(1) / df['FEEDER_CATTLE_FUTURES_TYPICAL_PRICE']
df['DIESEL_RATIO_L1'] = df['DIESEL_RETAIL_PRICE'].shift(1) / df['FEEDER_CATTLE_FUTURES_TYPICAL_PRICE']
# df['DIESEL_L4'] = df['DIESEL_RETAIL_PRICE'].shift(4)   # ~1 month lag

def plot_correlation_matrix(df, title):
    plt.figure(figsize=(8, 8))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)#, fmt='.2f', square=True, linewidths=0.5)
    plt.title(title)
    plt.tight_layout()
    plt.show()

plot_correlation_matrix(df,'')

target = df['AVG_PRICE_AUCTION']

plt.figure(figsize=(10, 5))
plt.plot(target.index, target, label='Target Feature')
plt.title('Average Auction Price over Time')
plt.ylabel('Average Auction Price')
plt.xlabel('Date')
plt.legend()
plt.savefig('target_feature_plot.png', dpi=300)
# plt.show()

df = df[['AVG_PRICE_AUCTION', 'US_MXN_RATES', 'ΔCPI', 'ΔFED', 'CORN_FEED_RATIO_L1', 'DIESEL_RATIO_L1', 'FEEDER_CATTLE_FUTURES_TYPICAL_PRICE']].dropna()
df.to_csv('model_features.csv')

