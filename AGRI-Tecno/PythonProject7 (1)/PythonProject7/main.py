"""
FastAPI Backend for AgriPredict - Soil and Yield Prediction
============================================================

This FastAPI application serves as the backend for the AgriPredict React frontend.
It exposes endpoints for:
  - Soil type prediction from images (CNN)
  - Yield prediction from soil parameters (Linear Regression)

Setup:
  1. Install dependencies: pip install -r requirements.txt
  2. Train yield model: python train_yield_model.py
  3. Run the server: uvicorn main:app --reload --port 8000

The server will be available at: http://localhost:8000
API documentation available at: http://localhost:8000/docs
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import io
from typing import Optional
import requests
from datetime import datetime

from ml_models import SoilClassifier, YieldPredictor
from schemas import (
    SoilPredictionResponse,
    YieldPredictionResponse,
    ErrorResponse,
)
from crop_data_manager import CropDataManager
from dynamic_prediction_engine import DynamicPredictionEngine
from crop_insights_generator import DynamicCropInsightsGenerator
from dynamic_ui_predictor import DynamicUIPredictor

# Confidence threshold below which we treat an image as not a soil photo
SOIL_CONFIDENCE_THRESHOLD = 0.7
# Minimum gap required between top1 and top2 probabilities to accept a prediction
SOIL_TOP2_GAP = 0.3

# ========================
# Initialize FastAPI App
# ========================

app = FastAPI(
    title="AgriPredict Backend API",
    description="Machine Learning backend for soil classification and yield prediction",
    version="1.0.0",
)

# ========================
# CORS Configuration
# ========================
# Allow requests from React frontend (adjust origin as needed for production)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],  # React dev servers & wildcard
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Initialize ML Models
# ========================

soil_classifier = None
yield_predictor = None
prediction_engine = None
insights_generator = None
ui_predictor = None


def initialize_models():
    """Load ML models on startup"""
    global soil_classifier, yield_predictor, prediction_engine, insights_generator, ui_predictor
    try:
        soil_classifier = SoilClassifier(checkpoint_path="checkpoints/best_model.pth")
        print("✓ Soil classification model loaded successfully")
    except Exception as e:
        print(f"✗ Error loading soil classifier: {e}")

    try:
        yield_predictor = YieldPredictor()  # Uses default model paths
        print("✓ Yield prediction model (XGBoost) loaded successfully")
    except Exception as e:
        print(f"✗ Error loading yield predictor: {e}")
    
    try:
        prediction_engine = DynamicPredictionEngine()
        print("✓ Dynamic prediction engine initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing prediction engine: {e}")
    
    try:
        insights_generator = DynamicCropInsightsGenerator()
        print("✓ Dynamic crop insights generator initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing insights generator: {e}")
    
    try:
        ui_predictor = DynamicUIPredictor()
        print("✓ Dynamic UI predictor initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing UI predictor: {e}")


@app.on_event("startup")
async def startup_event():
    """Run on server startup"""
    print("\n" + "="*50)
    print("AgriPredict Backend Starting...")
    print("="*50 + "\n")
    initialize_models()
    print("\n" + "="*50)
    print("Server Ready! 🚀")
    print("API Docs: http://localhost:8000/docs")
    print("="*50 + "\n")


# ========================
# Health Check Endpoint
# ========================

@app.get("/health", tags=["Health"])
async def health_check():
    """
    Check if the server and models are running.
    
    Returns:
        dict: Status of server and models
    """
    return {
        "status": "healthy",
        "soil_classifier_loaded": soil_classifier is not None,
        "yield_predictor_loaded": yield_predictor is not None,
    }


# ========================
# Soil Prediction Endpoint
# ========================

@app.post(
    "/predict-soil",
    response_model=SoilPredictionResponse,
    tags=["Predictions"],
    summary="Predict Soil Type from Image",
    description="Upload a soil image and get the predicted soil type classification"
)
async def predict_soil(file: UploadFile = File(...)):
    """
    Predict soil type from an uploaded image.
    
    Args:
        file: Image file (JPG, JPEG, PNG)
    
    Returns:
        SoilPredictionResponse: Predicted soil type and confidence
    
    Raises:
        HTTPException: If model not loaded, file is invalid, or prediction fails
    """
    # Validate model is loaded
    if soil_classifier is None:
        raise HTTPException(
            status_code=503,
            detail="Soil classification model not loaded. Please try again later."
        )

    # Validate file type
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload JPG or PNG image."
        )

    try:
        # Read image file
        contents = await file.read()
        image_data = io.BytesIO(contents)

        # Make prediction
        prediction = soil_classifier.predict(image_data)

        # If the top confidence is low, or the top-2 gap is small, assume the image is not a soil photo
        try:
            conf = float(prediction.get("confidence", 0.0))
        except Exception:
            conf = 0.0

        # Compute top2 gap from probabilities if available
        top_gap = 0.0
        try:
            probs = prediction.get("probabilities") or prediction.get("all_probabilities")
            if probs and isinstance(probs, dict):
                sorted_probs = sorted(probs.values(), reverse=True)
                if len(sorted_probs) >= 2:
                    top_gap = float(sorted_probs[0]) - float(sorted_probs[1])
        except Exception:
            top_gap = 0.0

        if conf < SOIL_CONFIDENCE_THRESHOLD or top_gap < SOIL_TOP2_GAP:
            raise HTTPException(
                status_code=400,
                detail="please upload your soil photo"
            )

        return SoilPredictionResponse(
            success=True,
            soil_type=prediction["soil_type"],
            confidence=prediction["confidence"],
            class_index=prediction["class_index"],
            all_probabilities=prediction["probabilities"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )


# ========================
# Yield Prediction Endpoint
# ========================

@app.post(
    "/predict-yield",
    response_model=YieldPredictionResponse,
    tags=["Predictions"],
    summary="Predict Crop Yield",
    description="Provide latitude and longitude; backend will fetch soil and weather data and return predicted yield"
)
async def predict_yield(
    lat: float = Form(..., description="Latitude of the location"),
    lon: float = Form(..., description="Longitude of the location"),
    weather_api_key: Optional[str] = Form(None, description="Optional weather API key (OpenWeatherMap style)")
):
    """
    Predict crop yield based on location. Fetches soil properties from SoilGrids
    and current weather (optionally via OpenWeatherMap) to build parameters.

    Args:
        lat: Latitude
        lon: Longitude
        weather_api_key: Optional API key for weather provider

    Returns:
        YieldPredictionResponse
    """
    # Validate model is loaded
    if yield_predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Yield prediction model not loaded. Please try again later."
        )

    try:
        # Helper: fetch SoilGrids properties
        def fetch_soilgrids(lat_v: float, lon_v: float) -> dict:
            url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={lat_v}&lon={lon_v}"
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            return r.json()

        soil_props = {}
        try:
            sg = fetch_soilgrids(lat, lon)
            props = sg.get("properties", {})

            # best-effort extraction: look for common keys
            def deep_find(d, keys):
                if not isinstance(d, dict):
                    return None
                for k in keys:
                    if k in d:
                        return d[k]
                for v in d.values():
                    res = deep_find(v, keys)
                    if res is not None:
                        return res
                return None

            n_val = deep_find(props, ["nitrogen", "n"])  # may be dict with 'values'
            ph_val = deep_find(props, ["phh2o", "ph"])   # pH

            def numeric_from(val):
                if val is None:
                    return None
                if isinstance(val, dict) and "values" in val:
                    vals = val.get("values")
                    if isinstance(vals, list) and vals:
                        return float(sum(vals) / len(vals))
                try:
                    return float(val)
                except Exception:
                    return None

            n_num = numeric_from(n_val)
            ph_num = numeric_from(ph_val)

            if n_num is not None:
                soil_props["nitrogen"] = float(n_num)
            if ph_num is not None:
                soil_props["ph"] = float(ph_num)

        except Exception as e:
            print(f"Warning: SoilGrids fetch failed: {e}")

        # Weather fetch (optional) - using OpenWeatherMap current weather endpoint
        weather = {}
        if weather_api_key:
            try:
                wurl = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}&units=metric"
                wr = requests.get(wurl, timeout=8)
                wr.raise_for_status()
                wj = wr.json()
                weather["temperature"] = wj.get("main", {}).get("temp")
                weather["humidity"] = wj.get("main", {}).get("humidity")
                rain_mm = 0.0
                if "rain" in wj:
                    rain_mm = wj["rain"].get("1h") or wj["rain"].get("3h") or 0.0
                weather["recent_rain_mm"] = rain_mm
            except Exception as e:
                print(f"Warning: weather fetch failed: {e}")

        # Assemble parameters with sensible defaults
        parameters = {
            "nitrogen": float(soil_props.get("nitrogen", 100.0)),
            "phosphorus": float(soil_props.get("phosphorus", 50.0)),
            "potassium": float(soil_props.get("potassium", 40.0)),
            "ph": float(soil_props.get("ph", 7.0)),
            "rainfall": float(soil_props.get("rainfall", 1000.0)),
        }

        if "temperature" in weather and weather["temperature"] is not None:
            parameters["temperature"] = float(weather["temperature"])
        if "humidity" in weather and weather["humidity"] is not None:
            parameters["humidity"] = float(weather["humidity"])

        # If rainfall not available, and we have recent rain, approximate annual
        if parameters.get("rainfall") == 1000.0 and weather.get("recent_rain_mm"):
            parameters["rainfall"] = max(200.0, min(2000.0, weather.get("recent_rain_mm", 0.0) * 365))

        prediction = yield_predictor.predict(parameters)

        return YieldPredictionResponse(
            success=True,
            predicted_yield=prediction["yield"],
            yield_unit="kg/ha",
            parameters=parameters,
            model_version=prediction.get("model_version", "1.0")
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid parameter values: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting yield: {str(e)}")


# ========================
# Comprehensive Crop Prediction Endpoint
# ========================

@app.post(
    "/predict-crop",
    tags=["Predictions"],
    summary="Predict Crop Yield with Full Form Data",
    description="Comprehensive endpoint accepting crop type, location, dates, farm size, irrigation, and soil image for tailored predictions"
)
async def predict_crop(
    crop: str = Form(..., description="Crop type (Rice, Maize, Groundnut, etc.)"),
    latitude: float = Form(..., description="Farm latitude"),
    longitude: float = Form(..., description="Farm longitude"),
    farm_size: float = Form(..., description="Farm size in acres"),
    sowing_date: str = Form(..., description="Sowing date (YYYY-MM-DD)"),
    irrigation_type: str = Form(..., description="Irrigation type (Rainfed, Drip, Sprinkler, Canal, Groundwater)"),
    previous_crop: Optional[str] = Form(None, description="Previously grown crop"),
    last_cultivation_date: Optional[str] = Form(None, description="Last cultivation date (YYYY-MM-DD)"),
    soil_image: UploadFile = File(..., description="Soil image file"),
    district: Optional[str] = Form(None, description="District name"),
    block: Optional[str] = Form(None, description="Block name"),
):
    """
    Comprehensive crop prediction using all farm parameters and soil image.
    
    Args:
        crop: Crop type
        latitude: Farm latitude
        longitude: Farm longitude
        farm_size: Farm size in acres
        sowing_date: Sowing date (ISO format)
        irrigation_type: Type of irrigation
        previous_crop: Previously grown crop (optional)
        last_cultivation_date: Last cultivation date (optional)
        soil_image: Soil image file
        district: District name (optional)
        block: Block name (optional)
    
    Returns:
        dict: Yield prediction with soil and crop-specific recommendations
    """
    if soil_classifier is None or yield_predictor is None:
        raise HTTPException(
            status_code=503,
            detail="One or more models not loaded. Please try again later."
        )

    try:
        # 1. Classify soil from image
        contents = await soil_image.read()
        image_data = io.BytesIO(contents)
        soil_prediction = soil_classifier.predict(image_data)
        soil_type = soil_prediction.get("soil_type", "Unknown")
        soil_confidence = soil_prediction.get("confidence", 0.0)

        # 2. Fetch soil properties from SoilGrids using coordinates
        soil_props = {}
        try:
            sg_url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={latitude}&lon={longitude}"
            sg = requests.get(sg_url, timeout=10).json()
            props = sg.get("properties", {})

            def deep_find(d, keys):
                if not isinstance(d, dict):
                    return None
                for k in keys:
                    if k in d:
                        return d[k]
                for v in d.values():
                    res = deep_find(v, keys)
                    if res is not None:
                        return res
                return None

            def numeric_from(val):
                if val is None:
                    return None
                if isinstance(val, dict) and "values" in val:
                    vals = val.get("values")
                    if isinstance(vals, list) and vals:
                        return float(sum(vals) / len(vals))
                try:
                    return float(val)
                except Exception:
                    return None

            n_val = deep_find(props, ["nitrogen", "n"])
            ph_val = deep_find(props, ["phh2o", "ph"])
            n_num = numeric_from(n_val)
            ph_num = numeric_from(ph_val)

            if n_num is not None:
                soil_props["nitrogen"] = float(n_num)
            if ph_num is not None:
                soil_props["ph"] = float(ph_num)

        except Exception as e:
            print(f"Warning: SoilGrids fetch failed: {e}")

        # 3. Convert farm size from acres to hectares for the model
        # 1 acre = 0.404686 hectares
        farm_size_hectares = farm_size * 0.404686

        # 4. Default/estimated values for features not directly provided
        # In real scenarios, these would come from user input or SoilGrids
        state = district or "Unknown"  # Use district as state for model
        season = "Kharif"  # Default; could be determined from sowing_date
        
        # Estimate reasonable defaults based on farm size and crop
        default_fertilizer_kg = farm_size_hectares * 150  # ~150 kg/hectare
        default_pesticide_kg = farm_size_hectares * 5     # ~5 kg/hectare
        default_rainfall_mm = 1200.0  # Default annual rainfall
        
        # Rough estimate of production based on typical yields
        # This will be overridden by model prediction anyway
        default_production_kg = farm_size_hectares * 2000  # ~2000 kg/hectare baseline

        # 5. Build prediction parameters for XGBoost model
        # These match the training data columns required by the pipeline
        parameters = {
            "crop": crop,
            "state": state,
            "season": season,
            "farm_size_hectares": farm_size_hectares,
            "fertilizer_kg": default_fertilizer_kg,
            "pesticide_kg": default_pesticide_kg,
            "rainfall_mm": default_rainfall_mm,
            "production_kg": default_production_kg,
            "year": datetime.now().year,
        }

        # 6. Get yield prediction from XGBoost model
        prediction = yield_predictor.predict(parameters)
        
        # Extract predictions (already in quintals/acre from YieldPredictor)
        quintals_per_acre = prediction.get("yield_quintals_per_acre", 0.0)
        total_yield = prediction.get("yield_total_quintals", 0.0)
        kg_per_ha = prediction.get("yield_kg_per_hectare", 0.0)
        success_rate = prediction.get("success_rate_percent", 75.0)

        return {
            "success": True,
            "crop": crop,
            "predicted_yield_kg_per_ha": round(kg_per_ha, 2),
            "predicted_yield_quintals_per_acre": round(quintals_per_acre, 2),
            "predicted_yield_total_quintals": round(total_yield, 2),
            "soil_type": soil_type,
            "soil_confidence": float(soil_confidence),
            "soil_parameters": {
                "state": state,
                "season": season,
                "farm_size_hectares": round(farm_size_hectares, 2),
            },
            "irrigation_type": irrigation_type,
            "farm_size_acres": farm_size,
            "sowing_date": sowing_date,
            "crop_specific_notes": f"Recommendations tailored for {crop} with {irrigation_type} irrigation on {soil_type} soil.",
            "success_rate_percent": round(success_rate, 1),
        }

    except Exception as e:
        print(f"Error in predict_crop: {e}")
        raise HTTPException(status_code=500, detail=f"Error predicting crop yield: {str(e)}")


# ========================
# Batch Prediction Endpoint (CSV Upload)
# ========================

@app.post(
    "/predict-yield-batch",
    tags=["Predictions"],
    summary="Batch Yield Prediction from CSV",
    description="Upload a CSV file with soil parameters for batch yield predictions"
)
async def predict_yield_batch(file: UploadFile = File(...)):
    """
    Predict yield for multiple soil samples from a CSV file.
    
    CSV should have columns: nitrogen, phosphorus, potassium, ph, rainfall
    Optional: temperature, humidity
    
    Args:
        file: CSV file with soil parameters
    
    Returns:
        dict: List of predictions for each row
    
    Raises:
        HTTPException: If model not loaded, file is invalid, or prediction fails
    """
    import csv

    if yield_predictor is None:
        raise HTTPException(
            status_code=503,
            detail="Yield prediction model not loaded."
        )

    if file.content_type != "text/csv":
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload CSV file."
        )

    try:
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_data = csv.DictReader(io.StringIO(decoded))

        results = []
        for row_idx, row in enumerate(csv_data):
            try:
                # If lat/lon are provided in CSV, fetch soil+weather for that location
                if row.get("lat") and row.get("lon"):
                    try:
                        lat = float(row.get("lat"))
                        lon = float(row.get("lon"))

                        # Fetch soilgrids
                        sg_url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={lat}&lon={lon}"
                        sg = requests.get(sg_url, timeout=10).json()
                        props = sg.get("properties", {})

                        def deep_find(d, keys):
                            if not isinstance(d, dict):
                                return None
                            for k in keys:
                                if k in d:
                                    return d[k]
                            for v in d.values():
                                res = deep_find(v, keys)
                                if res is not None:
                                    return res
                            return None

                        n_val = deep_find(props, ["nitrogen", "n"]) 
                        ph_val = deep_find(props, ["phh2o", "ph"]) 

                        def numeric_from(val):
                            if val is None:
                                return None
                            if isinstance(val, dict) and "values" in val:
                                vals = val.get("values")
                                if isinstance(vals, list) and vals:
                                    return float(sum(vals) / len(vals))
                            try:
                                return float(val)
                            except Exception:
                                return None

                        n_num = numeric_from(n_val)
                        ph_num = numeric_from(ph_val)

                        parameters = {
                            "nitrogen": float(n_num) if n_num is not None else 100.0,
                            "phosphorus": float(row.get("phosphorus", 50.0)),
                            "potassium": float(row.get("potassium", 40.0)),
                            "ph": float(ph_num) if ph_num is not None else float(row.get("ph", 7.0)),
                            "rainfall": float(row.get("rainfall", 1000.0)),
                        }
                        # optional: temperature/humidity in row
                        if row.get("temperature"):
                            parameters["temperature"] = float(row.get("temperature"))
                        if row.get("humidity"):
                            parameters["humidity"] = float(row.get("humidity"))

                    except Exception as e:
                        raise
                else:
                    parameters = {
                        "nitrogen": float(row.get("nitrogen", 0)),
                        "phosphorus": float(row.get("phosphorus", 0)),
                        "potassium": float(row.get("potassium", 0)),
                        "ph": float(row.get("ph", 7)),
                        "rainfall": float(row.get("rainfall", 0)),
                    }

                    if "temperature" in row and row["temperature"]:
                        parameters["temperature"] = float(row["temperature"])
                    if "humidity" in row and row["humidity"]:
                        parameters["humidity"] = float(row["humidity"])

                prediction = yield_predictor.predict(parameters)

                results.append({
                    "row": row_idx + 1,
                    "predicted_yield": prediction["yield"],
                    "parameters": parameters,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "row": row_idx + 1,
                    "status": "error",
                    "error": str(e)
                })

        return {
            "success": True,
            "total_rows": len(results),
            "predictions": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CSV: {str(e)}"
        )


# ========================
# Comprehensive Dynamic Prediction Endpoint (NO STATIC VALUES)
# ========================

@app.post(
    "/predict-comprehensive",
    tags=["Predictions"],
    summary="Comprehensive Dynamic Crop Prediction",
    description="Generate fully dynamic predictions based on soil image, location, weather, dataset, and APIs"
)
async def predict_comprehensive(
    crop: str = Form(..., description="Crop name (e.g., Rice, Wheat, Maize)"),
    latitude: float = Form(..., description="Farm latitude"),
    longitude: float = Form(..., description="Farm longitude"),
    farm_size_hectares: float = Form(..., description="Farm size in hectares"),
    sowing_date: str = Form(..., description="Sowing date (YYYY-MM-DD)"),
    irrigation_type: str = Form(..., description="Irrigation type (Rainfed, Drip, Sprinkler, Canal, Groundwater)"),
    soil_image: UploadFile = File(..., description="Soil image file"),
    weather_api_key: str = Form("", description="Optional OpenWeatherMap API key"),
):
    """
    Generate comprehensive dynamic prediction with ZERO static values.
    
    This endpoint:
    1. Classifies soil from image
    2. Fetches soil properties from SoilGrids API
    3. Fetches weather data (optional API)
    4. Loads crop statistics from yield dataset
    5. Calculates dynamic irrigation schedule
    6. Generates dynamic pest risks
    7. Computes dynamic costs/profits
    8. Creates dynamic growth stage schedule
    9. Suggests alternatives if yield < 60%
    
    Args:
        crop: Crop name
        latitude: Farm latitude
        longitude: Farm longitude
        farm_size_hectares: Farm size
        sowing_date: Sowing date
        irrigation_type: Irrigation type
        soil_image: Soil image file
        weather_api_key: Optional weather API key
    
    Returns:
        dict: Comprehensive dynamic prediction (all values computed, no statics)
    """
    
    if soil_classifier is None or prediction_engine is None:
        raise HTTPException(
            status_code=503,
            detail="Models not loaded. Please try again later."
        )
    
    try:
        # 1. Classify soil from image
        contents = await soil_image.read()
        image_data = io.BytesIO(contents)
        soil_prediction = soil_classifier.predict(image_data)
        soil_type = soil_prediction.get("soil_type", "Unknown Soil")
        soil_confidence = soil_prediction.get("confidence", 0.5)
        
        # 2. Generate comprehensive dynamic prediction
        api_key = weather_api_key if weather_api_key.strip() else None
        
        prediction = prediction_engine.generate_comprehensive_prediction(
            crop=crop,
            soil_type=soil_type,
            soil_model_confidence=soil_confidence,
            latitude=latitude,
            longitude=longitude,
            farm_size_hectares=farm_size_hectares,
            sowing_date=sowing_date,
            irrigation_type=irrigation_type,
            weather_api_key=api_key
        )
        
        # 3. Add metadata
        prediction["metadata"] = {
            "generated_at": datetime.now().isoformat(),
            "crop_selected": crop,
            "soil_classified": soil_type,
            "soil_image_confidence": soil_confidence,
            "location": {"latitude": latitude, "longitude": longitude},
            "farm_size": farm_size_hectares,
            "note": "All values dynamically calculated - NO static values used"
        }
        
        return {
            "success": True,
            "prediction": prediction
        }
    
    except Exception as e:
        import traceback
        print(f"Comprehensive prediction error: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating prediction: {str(e)}"
        )


# ========================
# Comprehensive Crop Insights Endpoint
# ========================

@app.post(
    "/crop-insights",
    tags=["Insights"],
    summary="Generate Comprehensive Crop Insights",
    description="Generate fully dynamic, crop-specific insights without any static values. Uses soil classification, dataset, and APIs."
)
async def crop_insights(
    crop: str = Form(..., description="Crop name (e.g., Rice, Wheat, Maize)"),
    soil_image_confidence: float = Form(0.85, description="Confidence of soil classification (0-1)"),
    farm_size_acres: float = Form(1.0, description="Farm size in acres"),
    latitude: float = Form(None, description="Farm latitude for SoilGrids API"),
    longitude: float = Form(None, description="Farm longitude for SoilGrids API"),
    sowing_date: str = Form(None, description="Sowing date (YYYY-MM-DD)"),
    season: str = Form("Kharif", description="Season (Kharif, Rabi, Summer)"),
    weather_api_key: str = Form(None, description="OpenWeatherMap API key (optional)"),
):
    """
    Generate comprehensive, 100% dynamic crop insights.
    
    NO STATIC VALUES - Everything is computed based on:
      1. Soil image classification model confidence
      2. Crop yield dataset statistics
      3. SoilGrids API soil properties
      4. Weather forecast data (if API key provided)
      5. Agronomic standards and best practices
    
    Returns JSON with:
      - Soil health suggestions (dynamic NPK, pH)
      - Irrigation schedule (7-day, weather-dependent)
      - Fertilizer recommendations (crop-specific splits)
      - Growth stage prediction (unique per crop)
      - Pest risk assessment (dataset-based)
      - Cost & profit estimates (dataset-derived)
      - Farming schedule (day-wise tasks)
      - Alternative crops (if yield < 60%)
    """
    
    if insights_generator is None:
        raise HTTPException(
            status_code=503,
            detail="Crop insights generator not loaded. Please try again later."
        )
    
    try:
        # Validate inputs
        if not crop or crop.strip() == "":
            raise ValueError("Crop name is required")
        
        soil_image_confidence = max(0, min(1, soil_image_confidence))
        farm_size_acres = max(0.1, farm_size_acres)
        
        # Generate comprehensive insights
        insights = insights_generator.generate_comprehensive_insights(
            crop=crop.strip(),
            soil_image_confidence=soil_image_confidence,
            farm_size_acres=farm_size_acres,
            latitude=latitude,
            longitude=longitude,
            sowing_date=sowing_date,
            season=season,
            weather_api_key=weather_api_key,
        )
        
        return {
            "success": True,
            "insights": insights
        }
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        import traceback
        print(f"Error generating crop insights: {e}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error generating crop insights: {str(e)}"
        )


# ========================
# Model Info Endpoint
# ========================

@app.get("/model-info", tags=["Info"])
async def model_info():
    """
    Get information about loaded models.
    
    Returns:
        dict: Details about soil classifier and yield predictor
    """
    return {
        "soil_classifier": {
            "name": "ResNet-18 Soil Classifier",
            "num_classes": 7,
            "classes": [
                "Alluvial Soil",
                "Arid Soil",
                "Black Soil",
                "Laterite Soil",
                "Mountain Soil",
                "Red Soil",
                "Yellow Soil"
            ],
            "input_size": "224x224 RGB image",
            "loaded": soil_classifier is not None
        },
        "yield_predictor": {
            "name": "Linear Regression Yield Predictor",
            "model_type": "sklearn LinearRegression",
            "input_features": ["nitrogen", "phosphorus", "potassium", "ph", "rainfall"],
            "optional_features": ["temperature", "humidity"],
            "output_unit": "kg/ha",
            "loaded": yield_predictor is not None
        }
    }


# ========================
# Root Endpoint
# ========================

@app.get("/", tags=["Root"])
async def root():
    """
    Welcome endpoint with API information.
    
    Returns:
        dict: API information and links
    """
    return {
        "message": "Welcome to AgriPredict Backend API",
        "version": "1.0.0",
        "documentation": "http://localhost:8000/docs",
        "redoc": "http://localhost:8000/redoc",
        "endpoints": {
            "health": "/health",
            "predict_soil": "/predict-soil (POST)",
            "predict_yield": "/predict-yield (POST)",
            "predict_yield_batch": "/predict-yield-batch (POST)",
            "predict_comprehensive": "/predict-comprehensive (POST) - NEW: Fully dynamic predictions",
            "model_info": "/model-info",
        }
    }


# ========================
# UI Predictions Endpoint
# ========================

@app.post(
    "/ui-predictions",
    tags=["UI"],
    summary="Get Dynamic UI Predictions (Growth Stages, Pests, Schedule)",
    description="Generate dynamic crop-specific UI predictions for growth stages, pest risks, and farming schedule without any static values."
)
async def get_ui_predictions(
    crop: str = Form(..., description="Crop name (e.g., Rice, Wheat, Maize)"),
    predicted_yield_percent: float = Form(70.0, description="Predicted yield percentage (0-100)"),
    humidity: float = Form(70.0, description="Relative humidity (%)"),
    temperature: float = Form(25.0, description="Temperature (°C)"),
    season: str = Form("Kharif", description="Season (Kharif/Rabi/Summer)"),
    sowing_date: str = Form(None, description="Sowing date (YYYY-MM-DD)"),
):
    """
    Generate dynamic UI predictions for the crop.
    
    Returns JSON with:
      - Crop growth stages (real biological stages with actual durations)
      - Pest risk assessment (actual pests for the crop with dynamic risk levels)
      - Farming schedule (realistic day-wise tasks for the crop cycle)
      - Season comparison (alternative crops if yield < 60%)
    
    All values are ZERO static placeholders - fully dynamic based on crop type and conditions.
    """
    try:
        if ui_predictor is None:
            raise HTTPException(
                status_code=503,
                detail="UI predictor not initialized. Please try again later."
            )
        
        # Generate all UI predictions
        predictions = ui_predictor.generate_ui_predictions(
            crop=crop,
            predicted_yield_percent=predicted_yield_percent,
            humidity=humidity,
            temperature=temperature,
            season=season,
            sowing_date=sowing_date
        )
        
        return {
            "success": True,
            "crop": crop,
            "predictions": predictions,
            "generated_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating UI predictions: {str(e)}"
        )


# ========================
# Error Handlers
# ========================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error"
        }
    )


# ========================
# Run Server
# ========================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
