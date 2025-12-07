#!/usr/bin/env python
"""Test pipeline with real data"""

import joblib
import pandas as pd

obj = joblib.load('models/pipeline_yield.pkl')
df = pd.read_csv('crop_yield_clean.csv')

print("CSV columns:", df.columns.tolist())
print("First row:")
print(df.iloc[0])

print("\n\nPipeline metadata:")
print("Numeric cols:", obj['numeric_columns'])
print("Categorical cols:", obj['categorical_columns'])

# Test with first row
print("\n\nTesting prediction on first row:")
test_df = df[obj['numeric_columns'] + obj['categorical_columns']].iloc[[0]]
print("Test dataframe:")
print(test_df)

pred = obj['pipeline'].predict(test_df)
print("\nPrediction result:", pred)
