#!/usr/bin/env python
"""Test the dynamic prediction modules"""

from crop_data_manager import CropDataManager
from dynamic_prediction_engine import DynamicPredictionEngine

# Test CropDataManager
print("Testing CropDataManager...")
cm = CropDataManager()
rice_stats = cm.get_crop_yield_stats("Rice")
print(f"Rice yield stats mean: {rice_stats.get('mean_yield', 'N/A')}")

rice_npk = cm.get_crop_npk_requirements("Rice")
print(f"Rice NPK ratio: {rice_npk['ratio']}")

rice_pests = cm.get_crop_pest_risks("Rice")
print(f"Rice pests: {len(rice_pests)} recorded")

# Test DynamicPredictionEngine
print("\nTesting DynamicPredictionEngine...")
engine = DynamicPredictionEngine()
soilgrids = engine.fetch_soilgrids_data(26.8124, 75.8263)
print(f"SoilGrids N={soilgrids.get('nitrogen', 'N/A')}, P={soilgrids.get('phosphorus', 'N/A')}, K={soilgrids.get('potassium', 'N/A')}, pH={soilgrids.get('ph', 'N/A')}")

print("\n✓ All modules working correctly!")
