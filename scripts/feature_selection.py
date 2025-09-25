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
     'NATIONAL_AUCTION_SALES', 
     'NATIONAL_TOTAL_SALES', 
     'TEXAS_AUCTION_SALES', 
     ], axis=1)

df['ΔCPI'] = df['CPI_US'].pct_change().bfill() * 100  # % change
df['ΔFED'] = df['FEDERAL_INTEREST_RATE'].diff().bfill()  # absolute change in rate
df['CORN_FEED_RATIO'] = df['CORN_FUTURES_TYPICAL_PRICE'] / df['FEEDER_CATTLE_FUTURES_TYPICAL_PRICE']
df['DIESEL_RATIO'] = df['DIESEL_RETAIL_PRICE'] / df['FEEDER_CATTLE_FUTURES_TYPICAL_PRICE']
df['DIESEL_LAG4'] = df['DIESEL_RETAIL_PRICE'].shift(4).bfill()   # ~1 month lag

def plot_correlation_matrix(df, title):
    plt.figure(figsize=(8, 8))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)#, fmt='.2f', square=True, linewidths=0.5)
    plt.title(title)
    plt.tight_layout()
    # plt.show()

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

df = df[['AVG_PRICE_AUCTION', 'FEEDER_CATTLE_FUTURES_TYPICAL_PRICE', 'US_MXN_RATES', 'ΔCPI', 'ΔFED', 'CORN_FEED_RATIO', 'DIESEL_RATIO']]
df.to_csv('model_features.csv')

