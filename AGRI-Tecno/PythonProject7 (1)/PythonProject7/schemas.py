"""
Pydantic Schemas for API Request/Response Validation
====================================================

These schemas define the structure of API requests and responses.
They provide automatic validation and OpenAPI documentation.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from enum import Enum


# ========================
# Soil Prediction
# ========================

class SoilPredictionResponse(BaseModel):
    """Response model for soil prediction endpoint"""
    
    success: bool = Field(
        ...,
        description="Whether prediction was successful"
    )
    soil_type: str = Field(
        ...,
        description="Predicted soil type classification"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score of the prediction (0-1)"
    )
    class_index: int = Field(
        ...,
        ge=0,
        le=6,
        description="Index of predicted class"
    )
    all_probabilities: Dict[str, float] = Field(
        ...,
        description="Probability distribution across all soil classes"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "soil_type": "Black Soil",
                "confidence": 0.95,
                "class_index": 2,
                "all_probabilities": {
                    "Alluvial Soil": 0.02,
                    "Arid Soil": 0.01,
                    "Black Soil": 0.95,
                    "Laterite Soil": 0.01,
                    "Mountain Soil": 0.00,
                    "Red Soil": 0.01,
                    "Yellow Soil": 0.00
                }
            }
        }


# ========================
# Yield Prediction
# ========================

class YieldPredictionResponse(BaseModel):
    """Response model for yield prediction endpoint"""
    
    success: bool = Field(
        ...,
        description="Whether prediction was successful"
    )
    predicted_yield: float = Field(
        ...,
        ge=0.0,
        description="Predicted crop yield"
    )
    yield_unit: str = Field(
        default="kg/ha",
        description="Unit of yield measurement"
    )
    parameters: Dict[str, float] = Field(
        ...,
        description="Input parameters used for prediction"
    )
    model_version: str = Field(
        default="1.0",
        description="Version of the prediction model"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "predicted_yield": 5242.5,
                "yield_unit": "kg/ha",
                "parameters": {
                    "nitrogen": 100.0,
                    "phosphorus": 50.0,
                    "potassium": 40.0,
                    "ph": 7.0,
                    "rainfall": 1000.0
                },
                "model_version": "1.0"
            }
        }


# ========================
# Error Responses
# ========================

class ErrorResponse(BaseModel):
    """Generic error response"""
    
    success: bool = Field(
        default=False,
        description="Whether request was successful"
    )
    error: str = Field(
        ...,
        description="Error message describing the issue"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Invalid file type. Please upload JPG or PNG image."
            }
        }


# ========================
# Batch Prediction
# ========================

class BatchPredictionResult(BaseModel):
    """Single result in batch prediction"""
    
    row: int = Field(
        ...,
        description="Row number in the CSV file"
    )
    status: str = Field(
        ...,
        description="Status of prediction: 'success' or 'error'"
    )
    predicted_yield: Optional[float] = Field(
        default=None,
        description="Predicted yield (if successful)"
    )
    parameters: Optional[Dict[str, float]] = Field(
        default=None,
        description="Input parameters (if successful)"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message (if failed)"
    )


class BatchPredictionResponse(BaseModel):
    """Response model for batch prediction endpoint"""
    
    success: bool = Field(
        ...,
        description="Whether batch processing was successful"
    )
    total_rows: int = Field(
        ...,
        description="Total number of rows processed"
    )
    predictions: List[BatchPredictionResult] = Field(
        ...,
        description="List of prediction results for each row"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "total_rows": 2,
                "predictions": [
                    {
                        "row": 1,
                        "status": "success",
                        "predicted_yield": 5242.5,
                        "parameters": {
                            "nitrogen": 100.0,
                            "phosphorus": 50.0,
                            "potassium": 40.0,
                            "ph": 7.0,
                            "rainfall": 1000.0
                        },
                        "error": None
                    },
                    {
                        "row": 2,
                        "status": "error",
                        "predicted_yield": None,
                        "parameters": None,
                        "error": "Missing required parameter: nitrogen"
                    }
                ]
            }
        }
