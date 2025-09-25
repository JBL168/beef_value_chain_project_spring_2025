import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

data = pd.read_csv('aggregated_data.csv')
data['DATE'] = pd.to_datetime(data['DATE'])
data = data.sort_values('DATE', ignore_index=True).set_index('DATE').drop( # drop columns not used for training
    ['avg_price_steers_ML1', 
     'avg_price_steers_ML1_2', 
     'avg_price_heifers_ML1', 
     'avg_price_heifers_ML1_2', 
     'NATIONAL_AUCTION_SALES', 
     'NATIONAL_TOTAL_SALES', 
     'TEXAS_AUCTION_SALES', 
     ], axis=1)

data['ΔCPI'] = data['CPI_US'].pct_change() * 100  # % change
data['ΔFED'] = data['FEDERAL_INTEREST_RATE'].diff()  # absolute change in rate

def plot_correlation_matrix(df, title):
    plt.figure(figsize=(8, 8))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', center=0)#, fmt='.2f', square=True, linewidths=0.5)
    plt.title(title)
    plt.tight_layout()
    plt.show()

plot_correlation_matrix(data,'')

target = data['AVG_PRICE_AUCTION']

plt.figure(figsize=(10, 5))
plt.plot(target.index, target, label='Target Feature')
plt.title('Average Auction Price over Time')
plt.ylabel('Average Auction Price')
plt.xlabel('Date')
plt.legend()
plt.savefig('target_feature_plot.png', dpi=300)
plt.show()

data = data[['AVG_PRICE_AUCTION', 'FEEDER_CATTLE_FUTURES_TYPICAL_PRICE', 'US_MXN_RATES', 'ΔCPI', 'ΔFED']]
data.to_csv('model_features.csv')

