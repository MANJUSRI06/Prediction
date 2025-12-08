"""
ML Models Wrapper Module
========================

This module provides wrapper classes for:
  - SoilClassifier: CNN-based soil type classification
  - YieldPredictor: Linear Regression-based yield prediction

These wrappers handle model loading, preprocessing, and inference.
"""

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import pickle
from pathlib import Path
from typing import Dict, List
import io
import warnings

warnings.filterwarnings("ignore")


# ========================
# Soil Classification Model
# ========================

class SoilClassifierModel(nn.Module):
    """ResNet-18 based soil classifier"""
    def __init__(self, num_classes):
        super(SoilClassifierModel, self).__init__()
        self.model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
        self.model.fc = nn.Linear(512, num_classes)

    def forward(self, x):
        return self.model(x)


class SoilClassifier:
    """
    Wrapper for soil classification model.
    
    Handles model loading, image preprocessing, and prediction.
    """
    
    # Soil class names (must match your training data folder order)
    CLASS_NAMES = [
        "Alluvial Soil",
        "Arid Soil",
        "Black Soil",
        "Laterite Soil",
        "Mountain Soil",
        "Red Soil",
        "Yellow Soil"
    ]
    
    NUM_CLASSES = len(CLASS_NAMES)
    IMG_SIZE = 224
    
    def __init__(self, checkpoint_path: str = "checkpoints/best_model.pth"):
        """
        Initialize the soil classifier.
        
        Args:
            checkpoint_path: Path to the saved model checkpoint
        
        Raises:
            FileNotFoundError: If checkpoint doesn't exist
            Exception: If model loading fails
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.checkpoint_path = checkpoint_path
        self.model = None
        
        self._load_model()
        self._setup_transforms()
    
    def _load_model(self):
        """Load the model from checkpoint"""
        checkpoint_path = Path(self.checkpoint_path)
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Checkpoint not found at: {self.checkpoint_path}")
        
        # Create model architecture
        self.model = SoilClassifierModel(num_classes=self.NUM_CLASSES)
        
        # Load checkpoint
        checkpoint = torch.load(self.checkpoint_path, map_location=self.device)
        
        # Handle checkpoint format variations
        if isinstance(checkpoint, dict):
            if "model" in checkpoint:
                state_dict = checkpoint["model"]
            elif "state_dict" in checkpoint:
                state_dict = checkpoint["state_dict"]
            else:
                state_dict = checkpoint
        else:
            state_dict = checkpoint
        
        # Clean state dict keys (remove "model." prefix if present)
        clean_state = {}
        for key, value in state_dict.items():
            new_key = key.replace("model.", "")
            clean_state[new_key] = value
        
        # Load state dict
        self.model.load_state_dict(clean_state, strict=False)
        self.model.to(self.device)
        self.model.eval()
    
    def _setup_transforms(self):
        """Setup image transformation pipeline"""
        self.transform = transforms.Compose([
            transforms.Resize((self.IMG_SIZE, self.IMG_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])
    
    def predict(self, image_input) -> Dict:
        """
        Predict soil type from an image.
        
        Args:
            image_input: Either a file path (str), PIL Image, or bytes object
        
        Returns:
            dict: Prediction results containing:
                - soil_type: Predicted soil class name
                - confidence: Confidence score (0-1)
                - class_index: Class index
                - probabilities: Probabilities for all classes
        
        Raises:
            ValueError: If image cannot be processed
        """
        try:
            # Load image
            if isinstance(image_input, str):
                image = Image.open(image_input).convert("RGB")
            elif isinstance(image_input, bytes):
                image = Image.open(io.BytesIO(image_input)).convert("RGB")
            elif isinstance(image_input, io.BytesIO):
                image = Image.open(image_input).convert("RGB")
            elif isinstance(image_input, Image.Image):
                image = image_input.convert("RGB")
            else:
                raise ValueError(f"Unsupported image input type: {type(image_input)}")
            
            # Transform and predict
            img_tensor = self.transform(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(img_tensor)
                probabilities = torch.softmax(outputs, dim=1)[0].cpu().numpy()
                class_idx = torch.argmax(outputs, dim=1).item()
            
            return {
                "soil_type": self.CLASS_NAMES[class_idx],
                "class_index": class_idx,
                "confidence": float(probabilities[class_idx]),
                "probabilities": {
                    name: float(prob)
                    for name, prob in zip(self.CLASS_NAMES, probabilities)
                }
            }
        
        except Exception as e:
            raise ValueError(f"Failed to process image: {str(e)}")


# ========================
# Yield Prediction Model
# ========================

class YieldPredictor:
    """
    Wrapper for trained yield prediction pipeline (trained on crop yield CSV data).
    
    Loads a scikit-learn pipeline that was trained on crop yield dataset with columns:
    - Numeric: Crop_Year, Area, Production, Annual_Rainfall, Fertilizer, Pesticide
    - Categorical: Crop, Season, State
    
    The pipeline includes preprocessing (StandardScaler, OneHotEncoder) and LinearRegression model.
    Returns yield predictions in kg/ha, converted to quintals/acre for user display.
    """
    
    # Expected input columns (raw data format - BEFORE one-hot encoding)
    REQUIRED_NUMERIC_COLS = ['Crop_Year', 'Area', 'Production', 'Annual_Rainfall', 'Fertilizer', 'Pesticide']
    REQUIRED_CATEGORICAL_COLS = ['Crop', 'Season', 'State']
    
    def __init__(self, model_paths: List[str] = None):
        """
        Initialize the yield predictor by loading the trained pipeline.
        
        Args:
            model_paths: List of paths to try for loading the model.
                         Defaults to standard locations in yield datasets folder.
        """
        if model_paths is None:
            # Default paths to search
            model_paths = [
                r"C:\Users\MANJUSRI\Downloads\yeild datasets for predicted\yeild datasets for predicted\models\best_pipeline_xgb.pkl",
                r"C:\Users\MANJUSRI\Downloads\yeild datasets for predicted\yeild datasets for predicted\models\pipeline_yield.pkl",
                r"../../../Downloads/yeild datasets for predicted/yeild datasets for predicted/models/pipeline_yield.pkl",
                r"models/pipeline_yield.pkl",
            ]
        
        self.pipeline = None
        self.metadata = {}
        self.numeric_columns = []
        self.categorical_columns = []
        
        self._load_model(model_paths)
    
    def _load_model(self, model_paths: List[str]):
        """
        Load the model from the first available path.
        
        Args:
            model_paths: List of paths to try
        
        Raises:
            ValueError: If no model can be loaded
        """
        import joblib
        
        for model_path in model_paths:
            try:
                model_path = Path(model_path)
                if not model_path.exists():
                    continue
                
                print(f"Loading model from: {model_path}")
                obj = joblib.load(str(model_path))
                
                # Handle different object formats
                if isinstance(obj, dict) and "pipeline" in obj:
                    self.pipeline = obj["pipeline"]
                    self.metadata = obj
                    self.numeric_columns = obj.get("numeric_columns", self.REQUIRED_NUMERIC_COLS)
                    self.categorical_columns = obj.get("categorical_columns", self.REQUIRED_CATEGORICAL_COLS)
                    print(f"✓ Model loaded successfully (format: dict with pipeline)")
                    print(f"  Numeric cols: {len(self.numeric_columns)}, Categorical cols: {len(self.categorical_columns)}")
                    return
                
                elif hasattr(obj, "predict"):
                    # It's a pipeline object directly
                    self.pipeline = obj
                    self.numeric_columns = self.REQUIRED_NUMERIC_COLS
                    self.categorical_columns = self.REQUIRED_CATEGORICAL_COLS
                    print(f"✓ Model loaded successfully (format: direct pipeline)")
                    return
                
            except Exception as e:
                print(f"Failed to load from {model_path}: {e}")
                continue
        
        raise ValueError("Could not load model from any of the provided paths")
    
    def predict(self, parameters: Dict) -> Dict:
        """
        Predict crop yield from user input parameters.
        
        Expected parameters (maps to CSV data columns):
        - crop: Crop name (e.g., "Rice", "Wheat")
        - state: State name (e.g., "Assam", "Punjab")
        - season: Season (e.g., "Kharif", "Rabi", "Whole Year")
        - farm_size_hectares: Farm area in hectares
        - fertilizer_kg: Total fertilizer used (kg)
        - pesticide_kg: Total pesticide used (kg)
        - rainfall_mm: Annual rainfall (mm)
        - production_kg: Expected/estimated production (kg)
        - year: Crop year (int)
        
        Returns:
            dict: Prediction result containing:
                - yield_kg_per_hectare: Predicted yield (kg/ha)
                - yield_quintals_per_acre: Predicted yield (quintals/acre)
                - yield_total_quintals: Total yield for farm
                - model_version: Pipeline model version
                - success_rate_percent: Confidence score (0-100%)
        
        Raises:
            ValueError: If required parameters are missing or model failed to load
        """
        if self.pipeline is None:
            raise ValueError("Model not loaded. Cannot make predictions.")
        
        try:
            import pandas as pd
            
            # Extract parameters with smart defaults based on training data statistics
            farm_size_hectares = float(parameters.get("farm_size_hectares", 1.0))
            crop_name = str(parameters.get("crop", "Rice"))
            state_name = str(parameters.get("state", "Assam"))
            season_name = str(parameters.get("season", "Kharif     "))  # Note: pad with spaces for matching training data
            year = int(parameters.get("year", 2024))
            
            # Ensure season has trailing spaces to match training data format
            # Training seasons: 'Autumn     ', 'Kharif     ', 'Rabi       ', 'Summer     ', 'Whole Year ', 'Winter     '
            season_map = {
                'Autumn': 'Autumn     ',
                'Autumn     ': 'Autumn     ',
                'Kharif': 'Kharif     ',
                'Kharif     ': 'Kharif     ',
                'Rabi': 'Rabi       ',
                'Rabi       ': 'Rabi       ',
                'Summer': 'Summer     ',
                'Summer     ': 'Summer     ',
                'Whole Year': 'Whole Year ',
                'Whole Year ': 'Whole Year ',
                'Winter': 'Winter     ',
                'Winter     ': 'Winter     ',
            }
            season_name = season_map.get(season_name, season_name + ' ' * (11 - len(season_name)))  # Pad to 11 chars
            
            # If production not provided, estimate based on farm size and typical yields
            # Training data shows median production = 13,804 kg, median area = 9,317 ha
            # This gives median yield ≈ 1.48 (production/area ratio)
            # For typical modern Indian agriculture: expect 15-30 quintals/hectare
            # Which is 1500-3000 kg/hectare
            if "production_kg" in parameters and parameters.get("production_kg", 0) > 0:
                production_kg = float(parameters["production_kg"])
            else:
                # Estimate production from farm size and typical yields
                # Using 2000 kg/hectare as baseline (20 quintals/hectare)
                baseline_yield_kg_per_ha = 2000.0
                production_kg = farm_size_hectares * baseline_yield_kg_per_ha
            
            # Defaults for other features (based on training data)
            fertilizer_kg = float(parameters.get("fertilizer_kg", farm_size_hectares * 500.0))
            pesticide_kg = float(parameters.get("pesticide_kg", farm_size_hectares * 20.0))
            rainfall_mm = float(parameters.get("rainfall_mm", 1000.0))
            
            # Build dataframe with exact column names expected by the pipeline
            row_dict = {
                'Crop_Year': year,
                'Area': farm_size_hectares,
                'Production': production_kg,
                'Annual_Rainfall': rainfall_mm,
                'Fertilizer': fertilizer_kg,
                'Pesticide': pesticide_kg,
                'Crop': crop_name,
                'Season': season_name,
                'State': state_name,
            }
            
            # Create dataframe with columns in the order expected by pipeline
            df = pd.DataFrame([row_dict])
            
            # Ensure numeric columns are float type
            for col in self.numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
            
            # Predict using the pipeline
            # The pipeline internally applies preprocessing and returns yield prediction
            prediction = self.pipeline.predict(df)[0]
            prediction = float(prediction)
            
            # The model predicts Yield = Production / Area (dimensionless ratio)
            # In some cases this can be negative due to model quirks
            # We'll clamp to reasonable minimum and treat as kg/ha
            prediction_kg_ha = max(0.5, prediction)  # Minimum 0.5 kg/ha to avoid zero yields
            
            # Convert kg/ha to quintals/acre
            # 1 quintal = 100 kg
            # 1 hectare = 2.471 acres
            quintals_per_hectare = prediction_kg_ha / 100.0
            quintals_per_acre = quintals_per_hectare * 2.471
            
            # Calculate total yield for farm
            total_yield_quintals = quintals_per_hectare * farm_size_hectares
            
            # Estimate success rate based on yield reasonableness
            # Typical crop yields range from 5-50 quintals/acre
            if 5 <= quintals_per_acre <= 50:
                success_rate = 85.0
            elif 2 <= quintals_per_acre < 5:
                success_rate = 70.0
            elif quintals_per_acre > 50:
                success_rate = 60.0
            else:
                success_rate = 50.0
            
            return {
                "yield_kg_per_hectare": float(prediction_kg_ha),
                "yield_quintals_per_acre": float(quintals_per_acre),
                "yield_total_quintals": float(total_yield_quintals),
                "model_version": "Pipeline-trained",
                "success_rate_percent": float(success_rate),
            }
        
        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            raise ValueError(f"Prediction failed: {str(e)}")
