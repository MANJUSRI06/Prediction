#!/usr/bin/env python
"""Debug the pipeline prediction"""

import joblib
import pandas as pd

obj = joblib.load('c:\\Users\\MANJUSRI\\Downloads\\yeild datasets for predicted\\yeild datasets for predicted\\models\\pipeline_yield.pkl')

# Create test dataframe with correct categorical formatting
test_data = {
    'Crop_Year': 2024,
    'Area': 1.0,
    'Production': 2000.0,
    'Annual_Rainfall': 1200.0,
    'Fertilizer': 500.0,
    'Pesticide': 20.0,
    'Crop': 'Rice',
    'Season': 'Kharif     ',
    'State': 'Assam',
}

df = pd.DataFrame([test_data])
print("Input data:")
print(df)
print("\nData types:")
print(df.dtypes)

print("\n\nPipeline steps:")
print(obj['pipeline'])

print("\n\nRunning prediction...")
try:
    pred = obj['pipeline'].predict(df)
    print(f"Prediction result: {pred}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
