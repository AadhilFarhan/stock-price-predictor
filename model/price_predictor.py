import pandas as pd
from prophet import Prophet
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt

# def train_predict_price(df):
#     df = df.reset_index()
#     # Rename 'Datetime' to 'Date' if necessary
#     if 'Datetime' in df.columns:
#         df.rename(columns={'Datetime': 'Date'}, inplace=True)

#     # Now select only Date and Close
#     df = df[['Date', 'Close']]
#     df.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)
#     # Ensure datetime and remove timezone
#     df['ds'] = pd.to_datetime(df['ds'], errors='coerce').dt.tz_localize(None)

#     print("df type:", type(df))
#     print("df columns:", df.columns)
#     print("df['y'] type:", type(df['y']))
#     print("df['y'] values:", df['y'])

#     # Convert 'y' to numeric and drop bad rows
#     df['y'] = pd.to_numeric(df['y'], errors='coerce')
#     df = df.dropna(subset=['ds', 'y'])

#     # Ensure correct types
#     if not isinstance(df['y'], pd.Series):
#         df['y'] = pd.Series(df['y'])

#     print(df)

#     model = Prophet(daily_seasonality=True)
#     model.fit(df)

#     future = model.make_future_dataframe(periods=5)
#     forecast = model.predict(future)

#     return forecast.iloc[-1]['yhat']

def train_predict_price(df):
    df = df.reset_index()

    # Flatten multi-level column names
    df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
    print(f"Flattened columns: {df.columns.tolist()}")  # Debug print

    # Detect the date and price columns
    date_col = next((col for col in df.columns if 'Date' in col), None)
    price_col = next((col for col in df.columns if 'Close' in col), None)

    if not date_col or not price_col:
        raise ValueError(f"Required columns not found. Got: {df.columns}")

    # Subset and rename for Prophet
    df = df[[date_col, price_col]]
    df.columns = ['ds', 'y']

    # Clean and convert
    df['ds'] = pd.to_datetime(df['ds'], errors='coerce').dt.tz_localize(None)
    df['y'] = pd.to_numeric(df['y'], errors='coerce')
    df = df.dropna(subset=['ds', 'y'])

    # Forecast
    model = Prophet(daily_seasonality=True)
    model.fit(df)

    future = model.make_future_dataframe(periods=5)
    forecast = model.predict(future)

    print(forecast.tail(20))

    return forecast.iloc[-1]['yhat']

def train_predict_price_new(df):
    df = df.reset_index()

    # Flatten multi-level column names
    df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
    print(f"Flattened columns: {df.columns.tolist()}")

    # Detect columns
    date_col = next((col for col in df.columns if 'Date' in col), None)
    close_col = next((col for col in df.columns if 'Close' in col), None)
    open_col = next((col for col in df.columns if 'Open' in col), None)
    low_col = next((col for col in df.columns if 'Low' in col), None)
    vol_col = next((col for col in df.columns if 'Volume' in col), None)

    if not date_col or not close_col:
        raise ValueError(f"Required columns not found. Got: {df.columns}")

    # Subset and rename
    df = df[[date_col, close_col, open_col, low_col, vol_col]]
    df.columns = ['ds', 'y', 'open', 'low', 'volume']

    # Clean data
    df['ds'] = pd.to_datetime(df['ds'], errors='coerce').dt.tz_localize(None)
    for col in ['y', 'open', 'low', 'volume']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.dropna()

    # Build Prophet model with regressors
    model = Prophet(daily_seasonality=True)
    model.add_regressor('open')
    model.add_regressor('low')
    model.add_regressor('volume')

    model.fit(df)

    # Create future dataframe
    future = model.make_future_dataframe(periods=5)
    
    # Add regressors to future
    future = future.merge(df[['ds', 'open', 'low', 'volume']], on='ds', how='left')

    # Fill missing future regressors with last known values
    for col in ['open', 'low', 'volume']:
        future[col] = future[col].ffill()

    forecast = model.predict(future)
    print(forecast.tail(20))

    return forecast.iloc[-1]['yhat']


def create_features(df):
    df = df.copy()
    df['hour'] = df['Date'].dt.hour
    df['dayofweek'] = df['Date'].dt.dayofweek
    df['day'] = df['Date'].dt.day
    df['month'] = df['Date'].dt.month

    # Lag features
    df['lag1'] = df['Close'].shift(1)
    df['lag2'] = df['Close'].shift(2)
    df['lag3'] = df['Close'].shift(3)

    # Rolling features
    df['rolling_mean_5'] = df['Close'].rolling(window=5).mean()
    df['rolling_std_5'] = df['Close'].rolling(window=5).std()
    df['rolling_mean_20'] = df['Close'].rolling(window=20).mean()
    df['rolling_std_20'] = df['Close'].rolling(window=20).std()

    df = df.dropna()
    return df

def train_xgb_predict_next_day(df):
    df['Date'] = pd.to_datetime(df['Date'])
    df = create_features(df)

    # Create a target column: next day's average price
    df['target'] = df['Close'].shift(-78)  # 78 = 6.5 hours × 12 (5-min intervals/hour)
    df = df.dropna()

    feature_cols = ['hour', 'dayofweek', 'day', 'month',
                    'lag1', 'lag2', 'lag3',
                    'rolling_mean_5', 'rolling_std_5',
                    'rolling_mean_20', 'rolling_std_20']

    X = df[feature_cols]
    y = df['target']

    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=False, test_size=0.2)

    model = XGBRegressor(n_estimators=100, learning_rate=0.1)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    print(f"MAE: {mae:.4f}")

    # # Plot
    # plt.figure(figsize=(10, 4))
    # plt.plot(y_test.values, label='Actual')
    # plt.plot(y_pred, label='Predicted')
    # plt.title('Next Day Price Prediction')
    # plt.legend()
    # plt.show()

    # Predict next day from latest known data
    latest_row = df.iloc[-1:]
    next_day_price = model.predict(latest_row[feature_cols])[0]
    print(f"Predicted next day's average price: {next_day_price:.2f}")
    return next_day_price
