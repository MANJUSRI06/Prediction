"""
Crop Data Manager Module
========================

Loads and manages crop yield dataset for dynamic predictions.
Provides methods to extract crop-specific insights, pest vulnerabilities,
growth stages, fertilizer requirements, and cost/profit analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings("ignore")
class CropDataManager:
    """
    Manages crop yield dataset and provides dynamic crop-specific insights.
    """
    
    # Default paths to search for dataset
    DEFAULT_PATHS = [
        r"C:\Users\MANJUSRI\Desktop\Prediction\AGRI-Tecno\yeild datasets for predicted\yeild datasets for predicted\crop_yield_clean.csv",
        r"C:\Users\MANJUSRI\Downloads\yeild datasets for predicted\yeild datasets for predicted\crop_yield_clean.csv",
        r"crop_yield_clean.csv",
    ]
    
    # Soil type to crop suitability mapping
    SOIL_CROP_SUITABILITY = {
        "Alluvial Soil": ["Rice", "Wheat", "Sugarcane", "Potato", "Maize"],
        "Black Soil": ["Cotton(lint)", "Jowar", "Groundnut", "Sugarcane", "Maize"],
        "Red Soil": ["Groundnut", "Ragi", "Maize", "Arhar/Tur", "Cassava"],
        "Laterite Soil": ["Coconut ", "Cashewnut", "Arecanut", "Cocoa", "Ragi"],
        "Mountain Soil": ["Tea", "Coffee", "Cardamom", "Turmeric", "Ginger"],
        "Arid Soil": ["Bajra", "Groundnut", "Castor seed", "Niger seed", "Mustard"],
        "Yellow Soil": ["Sugarcane", "Rice", "Maize", "Potato", "Coconut "],
    }
    
    # Crop to pest vulnerability mapping
    CROP_PEST_MAP = {
        "Rice": [
            {"pest": "Stem Borer", "risk": "High", "damage": "40-70%"},
            {"pest": "Leaf Blast", "risk": "High", "damage": "20-50%"},
            {"pest": "Brown Plant Hopper", "risk": "Medium", "damage": "10-30%"},
            {"pest": "Bacterial Blight", "risk": "Medium", "damage": "15-35%"},
        ],
        "Wheat": [
            {"pest": "Armyworm", "risk": "Medium", "damage": "15-25%"},
            {"pest": "Chinch Bug", "risk": "Low", "damage": "5-15%"},
            {"pest": "Hessian Fly", "risk": "Low", "damage": "3-10%"},
        ],
        "Maize": [
            {"pest": "Stem Borer", "risk": "High", "damage": "30-60%"},
            {"pest": "Fall Armyworm", "risk": "High", "damage": "20-50%"},
            {"pest": "Root Worm", "risk": "Medium", "damage": "10-25%"},
        ],
        "Cotton(lint)": [
            {"pest": "Bollworm", "risk": "High", "damage": "30-70%"},
            {"pest": "Jassid", "risk": "High", "damage": "20-40%"},
            {"pest": "Whitefly", "risk": "Medium", "damage": "15-30%"},
        ],
        "Groundnut": [
            {"pest": "Leaf Miner", "risk": "Medium", "damage": "20-35%"},
            {"pest": "Pod Borer", "risk": "High", "damage": "25-50%"},
            {"pest": "Thrips", "risk": "Low", "damage": "5-15%"},
        ],
        "Sugarcane": [
            {"pest": "Top Borer", "risk": "High", "damage": "20-40%"},
            {"pest": "Shoot Borer", "risk": "Medium", "damage": "15-30%"},
            {"pest": "Scale Insect", "risk": "Low", "damage": "5-15%"},
        ],
    }
    
    # Generic pests for unmapped crops
    DEFAULT_PESTS = [
        {"pest": "Leaf Eating Caterpillar", "risk": "Medium", "damage": "15-30%"},
        {"pest": "Aphids", "risk": "Low", "damage": "5-15%"},
        {"pest": "Mites", "risk": "Low", "damage": "3-10%"},
    ]
    
    # Crop growth stage duration mapping (in days)
    CROP_GROWTH_STAGES = {
        "Rice": {
            "Germination": (0, 7),
            "Seedling": (8, 20),
            "Vegetative": (21, 45),
            "Flowering": (46, 60),
            "Grain Filling": (61, 80),
            "Maturity": (81, 120),
        },
        "Wheat": {
            "Germination": (0, 5),
            "Seedling": (6, 15),
            "Tillering": (16, 35),
            "Booting": (36, 50),
            "Flowering": (51, 60),
            "Grain Filling": (61, 85),
            "Maturity": (86, 120),
        },
        "Maize": {
            "Germination": (0, 5),
            "Seedling": (6, 20),
            "Vegetative": (21, 50),
            "Tasseling": (51, 60),
            "Silking": (61, 70),
            "Grain Filling": (71, 90),
            "Maturity": (91, 110),
        },
        "Sugarcane": {
            "Germination": (0, 7),
            "Sprouting": (8, 30),
            "Tillering": (31, 90),
            "Grand Growth": (91, 180),
            "Maturation": (181, 330),
        },
        "Cotton(lint)": {
            "Germination": (0, 7),
            "Seedling": (8, 30),
            "Flowering": (31, 60),
            "Boll Formation": (61, 100),
            "Boll Maturation": (101, 150),
            "Harvest": (151, 180),
        },
    }
    
    # Crop to NPK requirement mapping (kg/hectare)
    CROP_NPK_REQUIREMENTS = {
        "Rice": {"N": 120, "P": 40, "K": 40, "ratio": "3:1:1"},
        "Wheat": {"N": 100, "P": 50, "K": 40, "ratio": "2.5:1:0.8"},
        "Maize": {"N": 150, "P": 60, "K": 40, "ratio": "3.75:1.5:1"},
        "Cotton(lint)": {"N": 120, "P": 60, "K": 60, "ratio": "2:1:1"},
        "Groundnut": {"N": 80, "P": 40, "K": 40, "ratio": "2:1:1"},
        "Sugarcane": {"N": 200, "P": 60, "K": 120, "ratio": "1.67:0.5:1"},
        "Potato": {"N": 150, "P": 75, "K": 150, "ratio": "1:0.5:1"},
    }
    
    def __init__(self, csv_path: Optional[str] = None):
        """
        Initialize CropDataManager and load dataset.
        
        Args:
            csv_path: Path to crop yield CSV. If None, searches default paths.
        """
        self.df = None
        self.csv_path = None
        self._load_dataset(csv_path)
    
    def _load_dataset(self, csv_path: Optional[str] = None):
        """Load crop yield dataset from file."""
        paths_to_try = [csv_path] if csv_path else self.DEFAULT_PATHS
        
        for path in paths_to_try:
            if path is None:
                continue
            try:
                p = Path(path)
                if p.exists():
                    self.df = pd.read_csv(p)
                    self.csv_path = path
                    print(f"✓ Crop dataset loaded from: {path}")
                    print(f"  Records: {len(self.df)}, Columns: {list(self.df.columns)}")
                    return
            except Exception as e:
                print(f"Failed to load from {path}: {e}")
        
        print("✗ Warning: Could not load crop yield dataset. Using synthetic data only.")
        self.df = pd.DataFrame()
    
    def get_crop_yield_stats(self, crop: str, season: Optional[str] = None, state: Optional[str] = None) -> Dict:
        """
        Get yield statistics for a crop from dataset.
        
        Args:
            crop: Crop name
            season: Season (optional)
            state: State (optional)
        
        Returns:
            dict: Yield statistics (mean, median, min, max, std)
        """
        if self.df is None or self.df.empty:
            # Return synthetic defaults
            return {
                "mean_yield": 2.5,
                "median_yield": 2.2,
                "min_yield": 0.5,
                "max_yield": 8.0,
                "std_yield": 1.5,
                "unit": "ratio (Production/Area)",
                "source": "synthetic"
            }
        
        try:
            # Normalize crop name (trim trailing spaces in data)
            crop_normalized = crop.strip()
            
            # Filter dataset
            mask = self.df["Crop"].str.strip() == crop_normalized
            
            if season:
                season_padded = season if len(season) > 8 else season.ljust(11)
                mask &= self.df["Season"].str.strip() == season.strip()
            
            if state:
                mask &= self.df["State"].str.strip() == state.strip()
            
            filtered = self.df[mask]
            
            if filtered.empty:
                return {
                    "mean_yield": 2.0,
                    "median_yield": 1.8,
                    "min_yield": 0.5,
                    "max_yield": 6.0,
                    "std_yield": 1.2,
                    "unit": "ratio",
                    "source": "default"
                }
            
            yield_col = filtered["Yield"]
            return {
                "mean_yield": float(yield_col.mean()),
                "median_yield": float(yield_col.median()),
                "min_yield": float(yield_col.min()),
                "max_yield": float(yield_col.max()),
                "std_yield": float(yield_col.std()),
                "unit": "ratio (Production/Area)",
                "sample_count": len(filtered),
                "source": "dataset"
            }
        
        except Exception as e:
            print(f"Error getting crop stats: {e}")
            return {
                "mean_yield": 2.0,
                "median_yield": 1.8,
                "min_yield": 0.5,
                "max_yield": 6.0,
                "std_yield": 1.2,
                "unit": "ratio",
                "source": "default"
            }
    
    def get_crop_average_cost_profit(self, crop: str) -> Dict:
        """
        Estimate cost and profit for a crop based on dataset.
        
        Args:
            crop: Crop name
        
        Returns:
            dict: Cost, revenue, profit estimates
        """
        if self.df is None or self.df.empty:
            # Return synthetic defaults
            return {
                "cost_per_hectare": 25000,
                "revenue_per_hectare": 45000,
                "profit_per_hectare": 20000,
                "roi_percent": 80.0,
                "source": "synthetic"
            }
        
        try:
            # Filter for crop
            crop_normalized = crop.strip()
            crop_data = self.df[self.df["Crop"].str.strip() == crop_normalized]
            
            if crop_data.empty:
                return {
                    "cost_per_hectare": 25000,
                    "revenue_per_hectare": 45000,
                    "profit_per_hectare": 20000,
                    "roi_percent": 80.0,
                    "source": "default"
                }
            
            # Get averages
            avg_fertilizer = crop_data["Fertilizer"].mean()
            avg_pesticide = crop_data["Pesticide"].mean()
            avg_production = crop_data["Production"].mean()
            avg_area = crop_data["Area"].mean()
            
            # Estimate costs per hectare
            cost_fertilizer_per_ha = (avg_fertilizer / avg_area) * 50 if avg_area > 0 else 15000
            cost_pesticide_per_ha = (avg_pesticide / avg_area) * 500 if avg_area > 0 else 2000
            cost_labor_per_ha = 5000  # Fixed labor cost
            cost_seed_per_ha = 2000
            cost_other_per_ha = 2000
            
            cost_per_hectare = cost_fertilizer_per_ha + cost_pesticide_per_ha + cost_labor_per_ha + cost_seed_per_ha + cost_other_per_ha
            
            # Estimate revenue based on yield and market price
            avg_yield = crop_data["Yield"].mean()  # ratio (Production/Area)
            
            # Market prices (INR per unit - assuming production in kg)
            crop_prices = {
                "Rice": 3000,  # per quintal
                "Wheat": 2500,
                "Maize": 2000,
                "Cotton(lint)": 5500,
                "Groundnut": 5000,
                "Sugarcane": 300,  # per quintal
                "Potato": 2500,
                "Arhar/Tur": 6000,
            }
            
            price_per_unit = crop_prices.get(crop_normalized, 3000)
            
            # Revenue = yield * price
            # Convert yield ratio to quintals/hectare
            quintals_per_hectare = avg_yield * 100  # rough estimate
            revenue_per_hectare = (quintals_per_hectare / 100) * price_per_unit * 100  # adjust for units
            
            # Profit = Revenue - Cost
            profit_per_hectare = revenue_per_hectare - cost_per_hectare
            roi_percent = (profit_per_hectare / cost_per_hectare * 100) if cost_per_hectare > 0 else 0
            
            return {
                "cost_per_hectare": max(15000, float(cost_per_hectare)),
                "revenue_per_hectare": max(30000, float(revenue_per_hectare)),
                "profit_per_hectare": float(profit_per_hectare),
                "roi_percent": float(roi_percent),
                "source": "dataset"
            }
        
        except Exception as e:
            print(f"Error calculating cost/profit: {e}")
            return {
                "cost_per_hectare": 25000,
                "revenue_per_hectare": 45000,
                "profit_per_hectare": 20000,
                "roi_percent": 80.0,
                "source": "default"
            }
    
    def get_crop_npk_requirements(self, crop: str) -> Dict:
        """
        Get NPK requirements for a crop.
        
        Args:
            crop: Crop name
        
        Returns:
            dict: NPK values and fertilizer split recommendation
        """
        crop_normalized = crop.strip()
        
        if crop_normalized in self.CROP_NPK_REQUIREMENTS:
            req = self.CROP_NPK_REQUIREMENTS[crop_normalized]
            return {
                "nitrogen": req["N"],
                "phosphorus": req["P"],
                "potassium": req["K"],
                "ratio": req["ratio"],
                "urea_kg_per_ha": req["N"] / 0.46,  # Urea is 46% nitrogen
                "dap_kg_per_ha": req["P"] / 0.46,   # DAP is ~46% P2O5
                "mop_kg_per_ha": req["K"] / 0.6,    # MOP is ~60% K2O
                "source": "standard"
            }
        
        # Default for unknown crops
        return {
            "nitrogen": 100,
            "phosphorus": 50,
            "potassium": 40,
            "ratio": "2.5:1.25:1",
            "urea_kg_per_ha": 217,
            "dap_kg_per_ha": 109,
            "mop_kg_per_ha": 67,
            "source": "default"
        }
    
    def get_crop_growth_stages(self, crop: str) -> List[Dict]:
        """
        Get growth stages for a crop.
        
        Args:
            crop: Crop name
        
        Returns:
            List of growth stages with duration
        """
        crop_normalized = crop.strip()
        
        if crop_normalized in self.CROP_GROWTH_STAGES:
            stages_dict = self.CROP_GROWTH_STAGES[crop_normalized]
            return [
                {
                    "stage": stage,
                    "day_start": days[0],
                    "day_end": days[1],
                    "duration_days": days[1] - days[0] + 1,
                    "management": self._get_stage_management(crop_normalized, stage)
                }
                for stage, days in stages_dict.items()
            ]
        
        # Generic stages for unknown crops
        return [
            {"stage": "Germination", "day_start": 0, "day_end": 7, "duration_days": 7, "management": "Keep soil moist"},
            {"stage": "Vegetative", "day_start": 8, "day_end": 40, "duration_days": 32, "management": "Monitor growth, irrigate regularly"},
            {"stage": "Flowering", "day_start": 41, "day_end": 60, "duration_days": 19, "management": "Apply flowering nutrients"},
            {"stage": "Fruiting/Pod Formation", "day_start": 61, "day_end": 90, "duration_days": 29, "management": "Support plants, manage pests"},
            {"stage": "Maturation", "day_start": 91, "day_end": 120, "duration_days": 29, "management": "Reduce irrigation, prepare for harvest"},
        ]
    
    def _get_stage_management(self, crop: str, stage: str) -> str:
        """Get management recommendations for a growth stage."""
        management_tips = {
            "Germination": "Keep soil consistently moist, maintain temperature",
            "Seedling": "Protect from pests, ensure adequate light",
            "Vegetative": "Regular irrigation, NPK fertilizer application, weed control",
            "Tillering": "Increase N fertilizer, manage water levels",
            "Booting": "Maintain irrigation, monitor for pests",
            "Flowering": "Ensure adequate potassium, prevent water stress",
            "Grain Filling": "Maintain moisture, monitor grain development",
            "Maturity": "Reduce irrigation, prepare for harvest",
            "Sprouting": "Maintain moisture for sprouting",
            "Grand Growth": "Heavy irrigation, apply fertilizers in splits",
            "Maturation": "Reduce water, concentrate sugars in canes",
            "Tasseling": "Critical stage, ensure full water availability",
            "Silking": "Monitor pollination, prevent pests",
            "Boll Formation": "Apply K fertilizer, manage pests intensively",
            "Boll Maturation": "Reduce nitrogen, monitor for pest incidence",
            "Harvest": "Prepare equipment, monitor readiness",
        }
        return management_tips.get(stage, "Monitor crop development, irrigate as needed")
    
    def get_crop_pest_risks(self, crop: str) -> List[Dict]:
        """
        Get pest risks for a crop.
        
        Args:
            crop: Crop name
        
        Returns:
            List of pest risks
        """
        crop_normalized = crop.strip()
        return self.CROP_PEST_MAP.get(crop_normalized, self.DEFAULT_PESTS)
    
    def get_alternative_crops(self, soil_type: str, yield_threshold: float = 0.6) -> List[Dict]:
        """
        Get alternative crops suitable for a soil type.
        
        Args:
            soil_type: Soil type
            yield_threshold: Yield confidence threshold
        
        Returns:
            List of alternative crops with improvement estimate
        """
        suitable_crops = self.SOIL_CROP_SUITABILITY.get(soil_type, ["Maize", "Wheat", "Groundnut"])
        
        alternatives = []
        for crop in suitable_crops[:3]:  # Top 3 alternatives
            stats = self.get_crop_yield_stats(crop)
            cost_profit = self.get_crop_average_cost_profit(crop)
            
            # Estimate improvement over current low yield
            improvement_percent = 12 + np.random.uniform(0, 5)  # 12-17%
            
            alternatives.append({
                "crop": crop,
                "soil_suitability": "High",
                "average_yield": stats.get("mean_yield", 2.0),
                "estimated_profit": cost_profit.get("profit_per_hectare", 20000),
                "yield_improvement_percent": improvement_percent,
            })
        
        return alternatives
    
    def get_farming_schedule(self, crop: str, sowing_date: str) -> List[Dict]:
        """
        Get day-wise farming schedule for a crop.
        
        Args:
            crop: Crop name
            sowing_date: Sowing date (YYYY-MM-DD)
        
        Returns:
            List of farming activities by day
        """
        from datetime import datetime, timedelta
        
        crop_normalized = crop.strip()
        growth_stages = self.get_crop_growth_stages(crop_normalized)
        
        try:
            sow_date = datetime.strptime(sowing_date, "%Y-%m-%d")
        except:
            sow_date = datetime.now()
        
        schedule = []
        
        # Pre-sowing activities
        schedule.append({
            "activity_day": -7,
            "date": (sow_date - timedelta(days=7)).strftime("%Y-%m-%d"),
            "activity": "Land Preparation",
            "description": "Plow, harrow, level field. Remove weeds and crop residue.",
            "priority": "High"
        })
        
        schedule.append({
            "activity_day": 0,
            "date": sow_date.strftime("%Y-%m-%d"),
            "activity": "Sowing",
            "description": "Sow seeds at recommended depth and spacing. Irrigate if dry.",
            "priority": "High"
        })
        
        # Growth stage activities
        current_day = 5
        for stage in growth_stages:
            day_end = stage["day_end"]
            activity_name = f"{stage['stage']} Stage"
            
            schedule.append({
                "activity_day": current_day,
                "date": (sow_date + timedelta(days=current_day)).strftime("%Y-%m-%d"),
                "activity": activity_name,
                "description": stage["management"],
                "priority": "Medium" if stage["stage"] != "Flowering" else "High"
            })
            
            current_day = day_end + 5
        
        # Harvest preparation
        last_stage = growth_stages[-1]["day_end"]
        schedule.append({
            "activity_day": last_stage,
            "date": (sow_date + timedelta(days=last_stage)).strftime("%Y-%m-%d"),
            "activity": "Harvest",
            "description": "Harvest when crop is mature. Use appropriate harvesting equipment.",
            "priority": "High"
        })
        
        return schedule
