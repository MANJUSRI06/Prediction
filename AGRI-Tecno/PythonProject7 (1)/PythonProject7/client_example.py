"""
Python Client Example - Using the FastAPI Backend
================================================

This script demonstrates how to call the FastAPI backend from Python.
Useful for testing and integration with other Python scripts.

Usage:
    python client_example.py
"""

import requests
import json
from pathlib import Path
from typing import Dict, Optional
import time

# API Configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30  # seconds


class AgriPredictClient:
    """Client for AgriPredict FastAPI backend"""

    def __init__(self, base_url: str = API_BASE_URL):
        """Initialize the client"""
        self.base_url = base_url
        self.session = requests.Session()

    def check_health(self) -> bool:
        """Check if the API is running"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ API not accessible: {e}")
            return False

    def predict_soil(self, image_path: str) -> Dict:
        """
        Predict soil type from an image

        Args:
            image_path: Path to the image file

        Returns:
            dict: Prediction result
        """
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        with open(image_path, "rb") as f:
            files = {"file": f}
            response = self.session.post(
                f"{self.base_url}/predict-soil",
                files=files,
                timeout=TIMEOUT,
            )

        if response.status_code != 200:
            raise Exception(f"API error: {response.json()}")

        return response.json()

    def predict_yield(self, **parameters) -> Dict:
        """
        Predict crop yield from soil parameters

        Args:
            nitrogen: Nitrogen content (kg/ha)
            phosphorus: Phosphorus content (kg/ha)
            potassium: Potassium content (kg/ha)
            ph: Soil pH level
            rainfall: Annual rainfall (mm)
            temperature: (Optional) Average temperature (°C)
            humidity: (Optional) Soil humidity (%)

        Returns:
            dict: Prediction result
        """
        response = self.session.post(
            f"{self.base_url}/predict-yield",
            data=parameters,
            timeout=TIMEOUT,
        )

        if response.status_code != 200:
            raise Exception(f"API error: {response.json()}")

        return response.json()

    def predict_yield_batch(self, csv_path: str) -> Dict:
        """
        Predict yield for multiple samples from a CSV file

        Args:
            csv_path: Path to CSV file

        Returns:
            dict: Batch prediction results
        """
        csv_path = Path(csv_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV not found: {csv_path}")

        with open(csv_path, "rb") as f:
            files = {"file": f}
            response = self.session.post(
                f"{self.base_url}/predict-yield-batch",
                files=files,
                timeout=TIMEOUT,
            )

        if response.status_code != 200:
            raise Exception(f"API error: {response.json()}")

        return response.json()

    def get_model_info(self) -> Dict:
        """Get information about the loaded models"""
        response = self.session.get(f"{self.base_url}/model-info", timeout=TIMEOUT)
        return response.json()


def example_soil_prediction(client: AgriPredictClient):
    """Example: Predict soil type from an image"""
    print("\n" + "="*60)
    print("EXAMPLE: SOIL PREDICTION")
    print("="*60)

    # Find a sample image in the dataset
    sample_images = list(Path("combined_dataset/train").glob("*/image*"))[:1]

    if not sample_images:
        print("❌ No sample images found in combined_dataset/train/")
        print("   Please ensure training dataset exists")
        return

    image_path = sample_images[0]
    print(f"📸 Image: {image_path}")

    try:
        result = client.predict_soil(str(image_path))

        print(f"\n✓ Soil Type: {result['soil_type']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"\n  All Probabilities:")
        for soil_type, prob in sorted(
            result["all_probabilities"].items(), key=lambda x: x[1], reverse=True
        ):
            print(f"    {soil_type}: {prob:.2%}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_yield_prediction(client: AgriPredictClient):
    """Example: Predict yield from soil parameters"""
    print("\n" + "="*60)
    print("EXAMPLE: YIELD PREDICTION")
    print("="*60)

    parameters = {
        "nitrogen": 100.0,
        "phosphorus": 50.0,
        "potassium": 40.0,
        "ph": 7.0,
        "rainfall": 1000.0,
        "temperature": 25.0,
        "humidity": 65.0,
    }

    print("📊 Input Parameters:")
    for key, value in parameters.items():
        print(f"   {key}: {value}")

    try:
        result = client.predict_yield(**parameters)

        print(f"\n✓ Predicted Yield: {result['predicted_yield']:.2f} {result['yield_unit']}")
        print(f"  Model Version: {result['model_version']}")

    except Exception as e:
        print(f"❌ Error: {e}")


def example_batch_prediction(client: AgriPredictClient):
    """Example: Batch yield prediction from CSV"""
    print("\n" + "="*60)
    print("EXAMPLE: BATCH YIELD PREDICTION")
    print("="*60)

    # Create a sample CSV file
    csv_data = """nitrogen,phosphorus,potassium,ph,rainfall,temperature,humidity
100,50,40,7.0,1000,25,65
150,75,60,6.5,1200,26,70
120,60,50,7.5,1100,24,60"""

    csv_path = "sample_predictions.csv"
    with open(csv_path, "w") as f:
        f.write(csv_data)

    print(f"📁 CSV File: {csv_path}")
    print("\nData:")
    print(csv_data)

    try:
        result = client.predict_yield_batch(csv_path)

        print(f"\n✓ Processed {result['total_rows']} rows")
        print("\nResults:")
        for pred in result["predictions"]:
            if pred["status"] == "success":
                print(f"  Row {pred['row']}: {pred['predicted_yield']:.2f} kg/ha")
            else:
                print(f"  Row {pred['row']}: ERROR - {pred['error']}")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Cleanup
        Path(csv_path).unlink(missing_ok=True)


def main():
    """Main function"""
    print("\n" + "="*60)
    print("AgriPredict FastAPI Client Example")
    print("="*60)

    client = AgriPredictClient()

    # Check if API is running
    print("\n🔍 Checking API health...")
    if not client.check_health():
        print("\n❌ API is not running!")
        print("   Start the server with: uvicorn main:app --reload --port 8000")
        return

    print("✓ API is running!")

    # Get model info
    print("\n📋 Model Information:")
    try:
        info = client.get_model_info()
        print(f"  Soil Classifier: {info['soil_classifier']['name']}")
        print(f"    Classes: {len(info['soil_classifier']['classes'])}")
        print(f"  Yield Predictor: {info['yield_predictor']['name']}")
        print(f"    Features: {', '.join(info['yield_predictor']['input_features'])}")
    except Exception as e:
        print(f"  Error: {e}")

    # Run examples
    example_soil_prediction(client)
    example_yield_prediction(client)
    example_batch_prediction(client)

    print("\n" + "="*60)
    print("Examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
