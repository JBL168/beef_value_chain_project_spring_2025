from scipy import stats
from sklearn.metrics import mean_absolute_percentage_error
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def plot_residual_analysis(actual, predicted, model_name="Model"):
    """
    Create comprehensive residual analysis plots for model evaluation
    
    Parameters:
    actual: array-like, actual values
    predicted: array-like, predicted values
    model_name: str, name of the model for plot titles
    """
    # Calculate residuals
    residuals = actual - predicted
    
    # Create a 2x3 subplot layout
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle(f'{model_name} - Residual Analysis', fontsize=16, fontweight='bold')
    
    # 1. Residuals vs Fitted Values
    axes[0, 0].scatter(predicted, residuals, alpha=0.6, s=30)
    axes[0, 0].axhline(y=0, color='red', linestyle='--', alpha=0.8)
    axes[0, 0].set_xlabel('Fitted Values')
    axes[0, 0].set_ylabel('Residuals')
    axes[0, 0].set_title('Residuals vs Fitted Values')
    axes[0, 0].grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(predicted, residuals, 1)
    p = np.poly1d(z)
    axes[0, 0].plot(predicted, p(predicted), "r--", alpha=0.8, linewidth=2)
    
    # 2. Q-Q Plot (Quantile-Quantile)
    stats.probplot(residuals, dist="norm", plot=axes[0, 1])
    axes[0, 1].set_title('Q-Q Plot (Normal Distribution)')
    axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Histogram of Residuals
    axes[0, 2].hist(residuals, bins=30, density=True, alpha=0.7, color='skyblue', edgecolor='black')
    axes[0, 2].set_xlabel('Residuals')
    axes[0, 2].set_ylabel('Density')
    axes[0, 2].set_title('Distribution of Residuals')
    axes[0, 2].grid(True, alpha=0.3)
    
    # Overlay normal distribution
    mu, sigma = np.mean(residuals), np.std(residuals)
    x = np.linspace(residuals.min(), residuals.max(), 100)
    axes[0, 2].plot(x, stats.norm.pdf(x, mu, sigma), 'r-', linewidth=2, label='Normal Distribution')
    axes[0, 2].legend()
    
    # 4. Residuals Over Time
    if hasattr(actual, 'index'):
        time_index = actual.index
    else:
        time_index = range(len(actual))
    
    axes[1, 0].plot(time_index, residuals, marker='o', markersize=3, alpha=0.7)
    axes[1, 0].axhline(y=0, color='red', linestyle='--', alpha=0.8)
    axes[1, 0].set_xlabel('Time')
    axes[1, 0].set_ylabel('Residuals')
    axes[1, 0].set_title('Residuals Over Time')
    axes[1, 0].grid(True, alpha=0.3)
    
    # 5. Actual vs Predicted
    min_val = min(actual.min(), predicted.min())
    max_val = max(actual.max(), predicted.max())
    axes[1, 1].scatter(actual, predicted, alpha=0.6, s=30)
    axes[1, 1].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
    axes[1, 1].set_xlabel('Actual Values')
    axes[1, 1].set_ylabel('Predicted Values')
    axes[1, 1].set_title('Actual vs Predicted')
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3)
    
    # 6. Residuals Statistics Box
    axes[1, 2].axis('off')
    
    # Calculate statistics
    mae = mean_absolute_error(actual, predicted)
    mse = mean_squared_error(actual, predicted)
    rmse = np.sqrt(mse)
    mape = mean_absolute_percentage_error(actual, predicted) * 100
    r2 = r2_score(actual, predicted)
    
    # Shapiro-Wilk test for normality
    shapiro_stat, shapiro_p = stats.shapiro(residuals)
    
    # Ljung-Box test for autocorrelation (if time series data)
    try:
        ljung_box = acorr_ljungbox(residuals, lags=10, return_df=True)
        ljung_p = ljung_box['lb_pvalue'].iloc[-1]
    except:
        ljung_p = None
    
    # Create statistics text
    stats_text = f"""
    Residual Statistics:
    ─────────────────────
    Mean: {np.mean(residuals):.4f}
    Std Dev: {np.std(residuals):.4f}
    Min: {np.min(residuals):.4f}
    Max: {np.max(residuals):.4f}

    Model Performance:
    ─────────────────────
    MAE: {mae:.4f}
    RMSE: {rmse:.4f}
    MAPE: {mape:.2f}%
    R²: {r2:.4f}

    Diagnostic Tests:
    ─────────────────────
    Shapiro-Wilk (Normality):
    Statistic: {shapiro_stat:.4f}
    p-value: {shapiro_p:.4f}
    {'✓ Normal' if shapiro_p > 0.05 else '✗ Not Normal'}
    """
    
    if ljung_p is not None:
        stats_text += f"""
        Ljung-Box (Independence):
        p-value: {ljung_p:.4f}
        {'✓ Independent' if ljung_p > 0.05 else '✗ Autocorrelated'}
        """
    
    axes[1, 2].text(0.1, 0.5, stats_text, fontsize=10, 
                    verticalalignment='center', fontfamily='monospace',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray", alpha=0.8))
    
    plt.tight_layout()
    return fig

def plot_autocorrelation_analysis(residuals, model_name="Model", lags=40):
    """
    Plot ACF and PACF of residuals to check for autocorrelation
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    fig.suptitle(f'{model_name} - Autocorrelation Analysis of Residuals', fontsize=14, fontweight='bold')
    
    # ACF plot
    plot_acf(residuals, lags=lags, ax=axes[0], alpha=0.05)
    axes[0].set_title('Autocorrelation Function (ACF)')
    axes[0].grid(True, alpha=0.3)
    
    # PACF plot
    plot_pacf(residuals, lags=lags, ax=axes[1], alpha=0.05)
    axes[1].set_title('Partial Autocorrelation Function (PACF)')
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

def plot_forecast_intervals(train_data, test_data, forecast_mean, conf_intervals, model_name="Model"):
    """
    Plot training data, test data, forecasts with confidence intervals
    """
    plt.figure(figsize=(15, 8))
    
    # Plot training data
    plt.plot(train_data.index, train_data, label='Training Data', color='blue', alpha=0.8)
    
    # Plot test data
    plt.plot(test_data.index, test_data, label='Actual Test Data', color='green', linewidth=2)
    
    # Plot forecast
    plt.plot(test_data.index, forecast_mean, label='Forecast', color='red', linestyle='--', linewidth=2)
    
    # Plot confidence intervals
    if conf_intervals is not None:
        plt.fill_between(test_data.index,
                        conf_intervals.iloc[:, 0],
                        conf_intervals.iloc[:, 1],
                        color='red', alpha=0.2,
                        label='95% Confidence Interval')
    
    plt.title(f'{model_name} - Forecast vs Actual', fontsize=14, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    return plt.gcf()
