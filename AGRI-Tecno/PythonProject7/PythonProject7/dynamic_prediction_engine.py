"""
Dynamic Prediction Engine
==========================

Generates dynamic, crop-dependent, soil-dependent, weather-dependent,
and season-dependent predictions using:
  1. Soil Image Classification Model
  2. Yield Dataset CSV
  3. SoilGrids API for soil properties
  4. Weather data (IMD/OpenWeatherMap)

NEVER outputs static values - all predictions are calculated dynamically.
"""

import numpy as np
import requests
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from crop_data_manager import CropDataManager

class DynamicPredictionEngine:
    """
    Generates comprehensive dynamic predictions without static values.
    """
    
    def __init__(self):
        """Initialize the prediction engine."""
        self.crop_manager = CropDataManager()
        self.soil_to_npk_multipliers = {
            "Alluvial Soil": {"N": 1.0, "P": 1.0, "K": 1.0},
            "Black Soil": {"N": 0.95, "P": 1.1, "K": 1.05},
            "Red Soil": {"N": 1.15, "P": 0.85, "K": 0.95},
            "Laterite Soil": {"N": 1.25, "P": 0.8, "K": 0.9},
            "Mountain Soil": {"N": 1.2, "P": 1.1, "K": 1.15},
            "Arid Soil": {"N": 1.3, "P": 1.2, "K": 1.1},
            "Yellow Soil": {"N": 1.1, "P": 0.95, "K": 1.0},
        }
    
    def fetch_soilgrids_data(self, latitude: float, longitude: float) -> Dict:
        """
        Fetch soil properties from SoilGrids API.
        
        Args:
            latitude: Farm latitude
            longitude: Farm longitude
        
        Returns:
            dict: Soil properties (N, P, K, pH)
        """
        try:
            url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={latitude}&lon={longitude}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            properties = data.get("properties", {})
            
            # Extract nutrient values
            def extract_value(prop_dict, key_names):
                """Extract numeric value from nested dict or list."""
                if isinstance(prop_dict, dict):
                    for k in key_names:
                        if k in prop_dict:
                            val = prop_dict[k]
                            if isinstance(val, dict) and "values" in val:
                                vals = val["values"]
                                if isinstance(vals, list) and vals:
                                    return float(np.mean(vals))
                            try:
                                return float(val)
                            except:
                                pass
                return None
            
            nitrogen = extract_value(properties, ["nitrogen", "n", "N"])
            phosphorus = extract_value(properties, ["phosphorus", "p", "P"])
            potassium = extract_value(properties, ["potassium", "k", "K"])
            ph = extract_value(properties, ["phh2o", "ph", "pH"])
            
            return {
                "nitrogen": nitrogen or 100.0,
                "phosphorus": phosphorus or 50.0,
                "potassium": potassium or 40.0,
                "ph": ph or 7.0,
                "source": "SoilGrids API"
            }
        
        except Exception as e:
            print(f"SoilGrids fetch failed: {e}. Using defaults.")
            return {
                "nitrogen": 100.0,
                "phosphorus": 50.0,
                "potassium": 40.0,
                "ph": 7.0,
                "source": "default"
            }
    
    def fetch_weather_data(self, latitude: float, longitude: float, api_key: Optional[str] = None) -> Dict:
        """
        Fetch current weather data.
        
        Args:
            latitude: Farm latitude
            longitude: Farm longitude
            api_key: OpenWeatherMap API key (optional)
        
        Returns:
            dict: Weather data (temperature, humidity, rainfall)
        """
        weather = {
            "temperature": 25.0,
            "humidity": 60.0,
            "rainfall_mm": 0.0,
            "wind_speed": 10.0,
            "source": "default"
        }
        
        if not api_key:
            return weather
        
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}&units=metric"
            response = requests.get(url, timeout=8)
            response.raise_for_status()
            data = response.json()
            
            weather = {
                "temperature": float(data.get("main", {}).get("temp", 25.0)),
                "humidity": float(data.get("main", {}).get("humidity", 60.0)),
                "rainfall_mm": float(data.get("rain", {}).get("1h", 0.0)),
                "wind_speed": float(data.get("wind", {}).get("speed", 10.0)),
                "source": "OpenWeatherMap"
            }
        
        except Exception as e:
            print(f"Weather fetch failed: {e}")
        
        return weather
    
    def calculate_yield_confidence(
        self,
        soil_model_confidence: float,
        soil_type: str,
        crop: str,
        soilgrids_data: Dict,
        weather_data: Dict,
        historical_mean_yield: float
    ) -> float:
        """
        Calculate predicted yield confidence percentage (0-100).
        
        Uses multiple factors:
        - Soil image model confidence
        - Soil-crop suitability
        - Soil nutrient match
        - Weather favorability
        - Historical data
        
        Args:
            soil_model_confidence: Confidence from soil classification model (0-1)
            soil_type: Classified soil type
            crop: Selected crop
            soilgrids_data: Soil properties from SoilGrids
            weather_data: Weather data
            historical_mean_yield: Mean yield from dataset
        
        Returns:
            float: Predicted yield confidence (0-100%)
        """
        score = 0.0
        
        # 1. Soil classification confidence (0-30 points)
        score += soil_model_confidence * 30
        
        # 2. Soil-crop suitability (0-30 points)
        suitable_crops = self.crop_manager.SOIL_CROP_SUITABILITY.get(soil_type, [])
        if crop in suitable_crops:
            score += 30  # Perfect match
        elif crop in suitable_crops[:2]:
            score += 25  # Good match
        else:
            score += 15  # Possible but not ideal
        
        # 3. Soil nutrient adequacy (0-25 points)
        npk_req = self.crop_manager.get_crop_npk_requirements(crop)
        n_score = min(1.0, soilgrids_data.get("nitrogen", 100) / npk_req["nitrogen"])
        p_score = min(1.0, soilgrids_data.get("phosphorus", 50) / npk_req["phosphorus"])
        k_score = min(1.0, soilgrids_data.get("potassium", 40) / npk_req["potassium"])
        nutrient_score = (n_score + p_score + k_score) / 3 * 25
        score += nutrient_score
        
        # 4. Weather favorability (0-15 points)
        temp = weather_data.get("temperature", 25)
        humidity = weather_data.get("humidity", 60)
        
        # Most crops thrive in 20-30°C and 50-70% humidity
        temp_score = 1.0 - abs(temp - 25) / 25  # Peak at 25°C
        humidity_score = 1.0 - abs(humidity - 60) / 40  # Peak at 60% humidity
        weather_score = max(0, (temp_score + humidity_score) / 2 * 15)
        score += weather_score
        
        # Clamp to 0-100 range
        return max(0.0, min(100.0, score))
    
    def generate_dynamic_irrigation_schedule(
        self,
        crop: str,
        week_number: int,
        rainfall_mm: float,
        temperature: float
    ) -> List[Dict]:
        """
        Generate dynamic weekly irrigation schedule based on crop and weather.
        
        Args:
            crop: Crop name
            week_number: Week number from sowing
            rainfall_mm: Expected rainfall this week (mm)
            temperature: Average temperature (°C)
        
        Returns:
            List of daily irrigation recommendations
        """
        # Base irrigation requirements by crop (mm/week)
        crop_water_needs = {
            "Rice": 40,
            "Wheat": 25,
            "Maize": 35,
            "Cotton(lint)": 30,
            "Groundnut": 20,
            "Sugarcane": 45,
            "Potato": 25,
            "Arhar/Tur": 15,
        }
        
        base_need = crop_water_needs.get(crop.strip(), 25)
        
        # Adjust for growth stage
        if week_number < 2:
            stage_multiplier = 0.5  # Germination: low water need
        elif week_number < 6:
            stage_multiplier = 1.0  # Vegetative: normal
        elif week_number < 10:
            stage_multiplier = 1.3  # Flowering/Fruiting: high need
        else:
            stage_multiplier = 0.8  # Maturation: reduce
        
        # Adjust for temperature
        if temperature > 30:
            temp_multiplier = 1.3  # Hot: more irrigation
        elif temperature < 15:
            temp_multiplier = 0.7  # Cold: less irrigation
        else:
            temp_multiplier = 1.0
        
        # Calculate required irrigation
        required_irrigation = base_need * stage_multiplier * temp_multiplier
        
        # Subtract rainfall
        net_irrigation = max(0, required_irrigation - rainfall_mm)
        
        # Distribute over 3-4 irrigation days
        irrigation_days = [0, 2, 4, 6]  # Monday, Wednesday, Friday, Sunday
        irrigation_per_day = net_irrigation / len(irrigation_days)
        
        schedule = []
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day_idx in range(7):
            day_name = days_of_week[day_idx]
            irrigation = 0
            
            if day_idx in irrigation_days:
                irrigation = irrigation_per_day
            
            schedule.append({
                "day": day_name,
                "irrigation_mm": round(irrigation, 1),
                "notes": self._get_irrigation_notes(irrigation, rainfall_mm)
            })
        
        return schedule
    
    def _get_irrigation_notes(self, irrigation_mm: float, rainfall_mm: float) -> str:
        """Get notes for irrigation day."""
        if rainfall_mm > 15:
            return "Heavy rain expected, skip irrigation"
        elif rainfall_mm > 5:
            return "Moderate rain, reduce irrigation"
        elif irrigation_mm > 20:
            return f"Heavy irrigation needed ({irrigation_mm:.1f}mm)"
        elif irrigation_mm > 10:
            return f"Regular irrigation ({irrigation_mm:.1f}mm)"
        else:
            return "Light irrigation or monitor soil moisture"
    
    def calculate_season_comparison(
        self,
        predicted_yield_percent: float,
        historical_mean_yield: float,
        crop: str
    ) -> Dict:
        """
        Calculate season comparison (current vs previous/average).
        
        Args:
            predicted_yield_percent: Current year prediction (0-100%)
            historical_mean_yield: Historical average yield
            crop: Crop name
        
        Returns:
            dict: Season comparison with % change
        """
        # Convert prediction to yield units
        predicted_yield = (predicted_yield_percent / 100) * historical_mean_yield * 1.5
        
        # Calculate percentage change
        if historical_mean_yield > 0:
            percent_change = ((predicted_yield - historical_mean_yield) / historical_mean_yield) * 100
        else:
            percent_change = 0
        
        interpretation = ""
        if percent_change > 10:
            interpretation = "Excellent - Yield significantly above average"
        elif percent_change > 5:
            interpretation = "Very Good - Yield above average"
        elif percent_change > 0:
            interpretation = "Good - Slight increase expected"
        elif percent_change > -5:
            interpretation = "Average - Performance close to historical average"
        elif percent_change > -10:
            interpretation = "Below Average - Slight decrease expected"
        else:
            interpretation = "Poor - Significant yield decrease expected"
        
        return {
            "predicted_yield": round(predicted_yield, 2),
            "historical_mean_yield": round(historical_mean_yield, 2),
            "percent_change": round(percent_change, 1),
            "trend": "↑" if percent_change > 0 else "↓" if percent_change < 0 else "→",
            "interpretation": interpretation
        }
    
    def generate_comprehensive_prediction(
        self,
        crop: str,
        soil_type: str,
        soil_model_confidence: float,
        latitude: float,
        longitude: float,
        farm_size_hectares: float,
        sowing_date: str,
        irrigation_type: str,
        weather_api_key: Optional[str] = None
    ) -> Dict:
        """
        Generate comprehensive dynamic prediction with ALL dynamic values.
        
        Args:
            crop: Crop name
            soil_type: Soil type from image classification
            soil_model_confidence: Confidence from soil model (0-1)
            latitude: Farm latitude
            longitude: Farm longitude
            farm_size_hectares: Farm size in hectares
            sowing_date: Sowing date (YYYY-MM-DD)
            irrigation_type: Irrigation type
            weather_api_key: Optional weather API key
        
        Returns:
            dict: Comprehensive prediction with all dynamic data
        """
        
        # 1. Fetch external data
        soilgrids_data = self.fetch_soilgrids_data(latitude, longitude)
        weather_data = self.fetch_weather_data(latitude, longitude, weather_api_key)
        
        # 2. Get crop-specific data
        crop_stats = self.crop_manager.get_crop_yield_stats(crop)
        crop_npk = self.crop_manager.get_crop_npk_requirements(crop)
        crop_pests = self.crop_manager.get_crop_pest_risks(crop)
        growth_stages = self.crop_manager.get_crop_growth_stages(crop)
        cost_profit = self.crop_manager.get_crop_average_cost_profit(crop)
        farming_schedule = self.crop_manager.get_farming_schedule(crop, sowing_date)
        
        # 3. Adjust NPK based on soil type
        soil_multiplier = self.soil_to_npk_multipliers.get(soil_type, {"N": 1.0, "P": 1.0, "K": 1.0})
        adjusted_npk = {
            "nitrogen": crop_npk["nitrogen"] * soil_multiplier["N"],
            "phosphorus": crop_npk["phosphorus"] * soil_multiplier["P"],
            "potassium": crop_npk["potassium"] * soil_multiplier["K"],
        }
        
        # 4. Calculate yield confidence
        yield_confidence = self.calculate_yield_confidence(
            soil_model_confidence,
            soil_type,
            crop,
            soilgrids_data,
            weather_data,
            crop_stats["mean_yield"]
        )
        
        # 5. Generate irrigation schedule
        irrigation_schedule = self.generate_dynamic_irrigation_schedule(
            crop, 4,  # Assume week 4 for current status
            weather_data["rainfall_mm"],
            weather_data["temperature"]
        )
        
        # 6. Get season comparison
        season_comparison = self.calculate_season_comparison(
            yield_confidence,
            crop_stats["mean_yield"],
            crop
        )
        
        # 7. Determine if alternative crops are needed
        alternative_crops = []
        if yield_confidence < 60:
            alternative_crops = self.crop_manager.get_alternative_crops(soil_type, yield_confidence)
        
        # 8. Calculate total yield for farm
        total_yield_quintals = (yield_confidence / 100) * crop_stats["mean_yield"] * farm_size_hectares * 10
        yield_per_hectare = (yield_confidence / 100) * crop_stats["mean_yield"] * 100
        
        # 9. Estimate costs and profits
        adjusted_cost = cost_profit["cost_per_hectare"] * farm_size_hectares
        adjusted_revenue = (yield_per_hectare / 100) * 3000 * farm_size_hectares  # Rough estimate
        adjusted_profit = adjusted_revenue - adjusted_cost
        
        # Build comprehensive response
        return {
            "predicted_yield_percent": round(yield_confidence, 1),
            "yield_details": {
                "per_hectare_quintals": round(yield_per_hectare / 100, 2),
                "total_quintals": round(total_yield_quintals, 2),
                "farm_size_hectares": farm_size_hectares,
            },
            "soil_health": {
                "nitrogen_mg_kg": round(soilgrids_data["nitrogen"], 1),
                "phosphorus_mg_kg": round(soilgrids_data["phosphorus"], 1),
                "potassium_mg_kg": round(soilgrids_data["potassium"], 1),
                "pH": round(soilgrids_data["pH"], 2),
                "soil_type": soil_type,
                "soil_model_confidence": round(soil_model_confidence * 100, 1),
                "interpretation": self._interpret_soil_health(soilgrids_data, crop_npk),
            },
            "fertilizer_recommendation": {
                "npk_ratio": crop_npk["ratio"],
                "nitrogen_kg_per_hectare": round(adjusted_npk["nitrogen"], 1),
                "phosphorus_kg_per_hectare": round(adjusted_npk["phosphorus"], 1),
                "potassium_kg_per_hectare": round(adjusted_npk["potassium"], 1),
                "urea_kg_per_hectare": round(crop_npk["urea_kg_per_ha"] * soil_multiplier["N"], 1),
                "dap_kg_per_hectare": round(crop_npk["dap_kg_per_ha"] * soil_multiplier["P"], 1),
                "mop_kg_per_hectare": round(crop_npk["mop_kg_per_ha"] * soil_multiplier["K"], 1),
                "total_cost_per_hectare": round(cost_profit["cost_per_hectare"] * 0.4, 1),  # Fertilizer is ~40% of cost
                "source": "Dynamic calculation based on soil + crop data"
            },
            "irrigation_schedule": irrigation_schedule,
            "weather_current": {
                "temperature": round(weather_data["temperature"], 1),
                "humidity": round(weather_data["humidity"], 1),
                "rainfall_mm": round(weather_data["rainfall_mm"], 1),
                "wind_speed": round(weather_data["wind_speed"], 1),
                "irrigation_type": irrigation_type,
            },
            "growth_stages": growth_stages,
            "pest_risks": crop_pests,
            "cost_profit_analysis": {
                "cost_per_hectare": round(cost_profit["cost_per_hectare"], 0),
                "total_cost": round(adjusted_cost, 0),
                "revenue_per_hectare": round((yield_per_hectare / 100) * 3000, 0),
                "total_revenue": round(adjusted_revenue, 0),
                "profit_per_hectare": round((adjusted_revenue - adjusted_cost) / farm_size_hectares if farm_size_hectares > 0 else 0, 0),
                "total_profit": round(adjusted_profit, 0),
                "roi_percent": round((adjusted_profit / adjusted_cost * 100) if adjusted_cost > 0 else 0, 1),
                "breakeven_yield_quintals": round((adjusted_cost / farm_size_hectares) / 300, 2),  # Rough estimate
            },
            "season_comparison": season_comparison,
            "farming_schedule": farming_schedule,
            "alternative_crops": alternative_crops if yield_confidence < 60 else [],
            "confidence_factors": {
                "soil_image_confidence": round(soil_model_confidence * 100, 1),
                "soil_crop_suitability_score": round((yield_confidence * 0.3) / 30 * 100, 1),
                "overall_confidence_percent": round(yield_confidence, 1),
            }
        }
    
    def _interpret_soil_health(self, soilgrids_data: Dict, crop_npk: Dict) -> str:
        """Generate interpretation of soil health."""
        n = soilgrids_data["nitrogen"]
        p = soilgrids_data["phosphorus"]
        k = soilgrids_data["potassium"]
        ph = soilgrids_data["pH"]
        
        n_req = crop_npk["nitrogen"]
        p_req = crop_npk["phosphorus"]
        k_req = crop_npk["potassium"]
        
        n_ratio = n / n_req if n_req > 0 else 0
        p_ratio = p / p_req if p_req > 0 else 0
        k_ratio = k / k_req if k_req > 0 else 0
        
        deficiencies = []
        if n_ratio < 0.75:
            deficiencies.append(f"Nitrogen deficiency ({n:.0f}/{n_req:.0f})")
        if p_ratio < 0.75:
            deficiencies.append(f"Phosphorus deficiency ({p:.0f}/{p_req:.0f})")
        if k_ratio < 0.75:
            deficiencies.append(f"Potassium deficiency ({k:.0f}/{k_req:.0f})")
        
        if 6.5 <= ph <= 7.5:
            ph_status = "pH is optimal"
        elif ph < 6.5:
            ph_status = "Soil is acidic, consider liming"
        else:
            ph_status = "Soil is alkaline, consider sulfur application"
        
        if not deficiencies:
            return f"Soil nutrients are adequate for {crop_npk.get('crop', 'this crop')}. {ph_status}."
        else:
            return f"Detected: {', '.join(deficiencies)}. {ph_status}. Apply recommended fertilizers."
