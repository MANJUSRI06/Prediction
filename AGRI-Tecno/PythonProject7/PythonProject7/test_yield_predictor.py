#!/usr/bin/env python
"""Test script for YieldPredictor"""

from ml_models import YieldPredictor

try:
    print("Loading YieldPredictor...")
    predictor = YieldPredictor()
    print("✓ YieldPredictor loaded successfully")
    
    # Test prediction
    # NOTE: Categorical values must match training data exactly (including spaces!)
    params = {
        "crop": "Rice",
        "state": "Assam",
        "season": "Kharif     ",  # Note: trailing spaces match training data!
        "farm_size_hectares": 1.0,
        "fertilizer_kg": 500.0,  # 500 kg/hectare is realistic
        "pesticide_kg": 20.0,
        "rainfall_mm": 1200.0,
        "production_kg": 2000.0,  # 2000 kg from 1 hectare
        "year": 2024,
    }
    
    print("Making prediction with params:")
    for k, v in params.items():
        print(f"  {k}: {repr(v)}")
    
    result = predictor.predict(params)
    print("✓ Prediction successful!")
    print("Result:", result)
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
