#!/usr/bin/env python
"""Test with realistic training data values"""

import joblib
import pandas as pd

obj = joblib.load('c:\\Users\\MANJUSRI\\Downloads\\yeild datasets for predicted\\yeild datasets for predicted\\models\\pipeline_yield.pkl')

# Use actual data from training set (Rice from Assam, Autumn season)
test_data = {
    'Crop_Year': 1997,
    'Area': 607358.0,
    'Production': 398311.0,
    'Annual_Rainfall': 2000.0,
    'Fertilizer': 1000000.0,
    'Pesticide': 30000.0,
    'Crop': 'Rice',
    'Season': 'Autumn     ',  # Note: trailing spaces!
    'State': 'Assam',
}

df = pd.DataFrame([test_data])
print("Input data (from training set):")
print(df)

print("\n\nRunning prediction...")
pred = obj['pipeline'].predict(df)
print(f"Model prediction: {pred[0]:.4f}")

# The actual yield in the data was 0.780870
print(f"Actual yield from training data: 0.780870")
print(f"Difference: {pred[0] - 0.780870:.4f}")
