import pandas as pd
from prophet import Prophet

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

    print(forecast)

    return forecast.iloc[-1]['yhat']
