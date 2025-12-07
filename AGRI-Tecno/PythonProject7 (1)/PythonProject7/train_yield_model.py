"""
Yield Model Training Script
==========================

This script trains a Linear Regression model for crop yield prediction.
It uses soil parameters like nitrogen, phosphorus, potassium, pH, and rainfall.

Usage:
    python train_yield_model.py

Output:
    - models/yield_model.pkl: Trained model file
    - models/yield_model_info.txt: Model information
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from pathlib import Path
import pickle
import json


# ========================
# Configuration
# ========================

FEATURES = ["nitrogen", "phosphorus", "potassium", "ph", "rainfall"]
OUTPUT_DIR = Path("models")
MODEL_PATH = OUTPUT_DIR / "yield_model.pkl"


# ========================
# Synthetic Dataset Generator
# ========================

def generate_synthetic_data(n_samples: int = 1000) -> tuple:
    """
    Generate synthetic soil and yield data.
    
    This is used if you don't have a real dataset.
    Real data would come from agricultural surveys.
    
    Args:
        n_samples: Number of samples to generate
    
    Returns:
        tuple: (X, y) where X is features and y is yield
    """
    np.random.seed(42)
    
    # Generate synthetic features with realistic ranges
    nitrogen = np.random.uniform(50, 200, n_samples)      # kg/ha
    phosphorus = np.random.uniform(20, 80, n_samples)     # kg/ha
    potassium = np.random.uniform(30, 150, n_samples)     # kg/ha
    ph = np.random.uniform(5.5, 8.5, n_samples)           # pH level
    rainfall = np.random.uniform(400, 2000, n_samples)    # mm
    
    # Combine features
    X = np.column_stack([nitrogen, phosphorus, potassium, ph, rainfall])
    
    # Generate yield with realistic relationships
    # Yield increases with nutrients (nitrogen, phosphorus, potassium)
    # Yield has optimal pH (around 7)
    # Yield increases with rainfall (up to a limit)
    y = (
        0.5 * nitrogen +
        0.8 * phosphorus +
        0.6 * potassium +
        500 * np.exp(-((ph - 7) ** 2)) +  # Optimal at pH 7
        2 * rainfall +
        np.random.normal(0, 200, n_samples)  # Add noise
    )
    
    # Ensure non-negative yields
    y = np.maximum(y, 1000)
    
    return X, y


# ========================
# Load Real Data
# ========================

def load_real_data(csv_path: str) -> tuple:
    """
    Load real yield data from a CSV file.
    
    CSV should have columns: nitrogen, phosphorus, potassium, ph, rainfall, yield
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        tuple: (X, y) where X is features and y is yield
    """
    df = pd.read_csv(csv_path)
    
    # Extract features and target
    X = df[FEATURES].values
    y = df["yield"].values
    
    return X, y


# ========================
# Train Model
# ========================

def train_yield_model(X: np.ndarray, y: np.ndarray):
    """
    Train a Linear Regression model for yield prediction.
    
    Args:
        X: Feature matrix (n_samples, n_features)
        y: Target values (n_samples,)
    
    Returns:
        tuple: (model, scaler) - trained model and feature scaler
    """
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42
    )
    
    # Scale features for better performance
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    model = LinearRegression()
    model.fit(X_train_scaled, y_train)
    
    # Evaluate
    y_pred_train = model.predict(X_train_scaled)
    y_pred_test = model.predict(X_test_scaled)
    
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    # Print results
    print("\n" + "="*50)
    print("YIELD MODEL TRAINING RESULTS")
    print("="*50)
    print(f"\nTraining Metrics:")
    print(f"  R² Score: {train_r2:.4f}")
    print(f"  RMSE: {train_rmse:.2f} kg/ha")
    print(f"  MAE: {train_mae:.2f} kg/ha")
    
    print(f"\nTest Metrics:")
    print(f"  R² Score: {test_r2:.4f}")
    print(f"  RMSE: {test_rmse:.2f} kg/ha")
    print(f"  MAE: {test_mae:.2f} kg/ha")
    
    print(f"\nModel Coefficients:")
    for feature, coef in zip(FEATURES, model.coef_):
        print(f"  {feature}: {coef:.4f}")
    print(f"  Intercept: {model.intercept_:.2f}")
    print("="*50 + "\n")
    
    return model, scaler, {
        "train_r2": float(train_r2),
        "test_r2": float(test_r2),
        "train_rmse": float(train_rmse),
        "test_rmse": float(test_rmse),
        "train_mae": float(train_mae),
        "test_mae": float(test_mae),
    }


# ========================
# Save Model
# ========================

def save_model(model, scaler, metrics: dict):
    """
    Save the trained model and metadata.
    
    Args:
        model: Trained sklearn model
        scaler: Fitted StandardScaler
        metrics: Dictionary of evaluation metrics
    """
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save model with metadata
    save_data = {
        "model": model,
        "scaler": scaler,
        "feature_names": FEATURES,
        "metrics": metrics
    }
    
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(save_data, f)
    
    print(f"✓ Model saved to: {MODEL_PATH}")
    
    # Save model info as text
    info_path = OUTPUT_DIR / "yield_model_info.txt"
    with open(info_path, "w") as f:
        f.write("YIELD PREDICTION MODEL\n")
        f.write("="*50 + "\n\n")
        f.write(f"Input Features: {', '.join(FEATURES)}\n")
        f.write(f"Output: Crop Yield (kg/ha)\n")
        f.write(f"Model Type: Linear Regression\n\n")
        f.write("Coefficients:\n")
        for feature, coef in zip(FEATURES, model.coef_):
            f.write(f"  {feature}: {coef:.4f}\n")
        f.write(f"  Intercept: {model.intercept_:.2f}\n\n")
        f.write("Performance Metrics:\n")
        f.write(f"  Test R² Score: {metrics['test_r2']:.4f}\n")
        f.write(f"  Test RMSE: {metrics['test_rmse']:.2f} kg/ha\n")
        f.write(f"  Test MAE: {metrics['test_mae']:.2f} kg/ha\n")
    
    print(f"✓ Model info saved to: {info_path}")


# ========================
# Main
# ========================

def main():
    """Main training function"""
    print("\n" + "="*50)
    print("TRAINING YIELD PREDICTION MODEL")
    print("="*50 + "\n")
    
    # Check for existing data
    csv_path = "yield_data.csv"
    
    if Path(csv_path).exists():
        print(f"Loading data from {csv_path}...")
        X, y = load_real_data(csv_path)
    else:
        print("Generating synthetic data (no yield_data.csv found)...")
        print("To use real data, create a CSV file with columns:")
        print("  nitrogen, phosphorus, potassium, ph, rainfall, yield\n")
        X, y = generate_synthetic_data(n_samples=1000)
    
    print(f"Loaded {len(X)} samples with {len(FEATURES)} features\n")
    
    # Train model
    model, scaler, metrics = train_yield_model(X, y)
    
    # Save model
    save_model(model, scaler, metrics)
    
    # Test prediction
    print("Testing prediction with sample data:")
    sample = np.array([[100, 50, 40, 7.0, 1000]])  # Sample input
    sample_scaled = scaler.transform(sample)
    prediction = model.predict(sample_scaled)[0]
    print(f"  Input: N=100, P=50, K=40, pH=7.0, Rainfall=1000")
    print(f"  Predicted Yield: {prediction:.2f} kg/ha\n")


if __name__ == "__main__":
    main()
