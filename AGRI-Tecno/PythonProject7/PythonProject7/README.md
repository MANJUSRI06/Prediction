# AgriPredict Backend API - Complete Setup Guide

A **FastAPI** backend for connecting your React frontend with Python ML models for soil classification and crop yield prediction.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Installation](#installation)
5. [Running the Server](#running-the-server)
6. [API Endpoints](#api-endpoints)
7. [Integration with React](#integration-with-react)
8. [Example Usage](#example-usage)
9. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This backend provides REST API endpoints that:
- **Classify soil types** from uploaded images using a CNN (ResNet-18)
- **Predict crop yield** from soil parameters using Linear Regression
- Handle batch processing from CSV files
- Serve predictions with detailed confidence scores and probability distributions

---

## ✨ Features

✅ **Image Classification**
- Upload soil images (JPG/PNG)
- Get soil type predictions with confidence scores
- Receive probability distribution across all soil classes

✅ **Yield Prediction**
- Single and batch prediction modes
- Input parameters: Nitrogen, Phosphorus, Potassium, pH, Rainfall
- Optional parameters: Temperature, Humidity

✅ **Production-Ready**
- CORS enabled for React frontend communication
- Comprehensive error handling
- Automatic API documentation (Swagger UI)
- Health check endpoints
- Model loading verification

✅ **Well-Structured Code**
- Modular architecture for easy maintenance
- Type hints for better IDE support
- Clear separation of concerns
- Well-documented functions

---

## 📁 Project Structure

```
PythonProject7/
├── main.py                        # FastAPI application (START HERE)
├── ml_models.py                   # ML model wrappers (SoilClassifier, YieldPredictor)
├── schemas.py                     # Pydantic schemas for request/response validation
├── train_yield_model.py           # Yield model training script
├── client_example.py              # Python client example
├── react_api_client.js            # React custom hook for API calls
├── SoilPredictionComponent.tsx     # Example React component (soil prediction)
├── YieldPredictionComponent.tsx    # Example React component (yield prediction)
├── requirements.txt               # Python dependencies
├── checkpoints/
│   └── best_model.pth            # Pre-trained soil classifier (CNN)
├── models/
│   └── yield_model.pkl           # Pre-trained yield prediction model
└── README.md                      # This file
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- CUDA (optional, for GPU acceleration)

### Step 1: Install Dependencies

Navigate to the `PythonProject7` directory and install required packages:

```bash
cd PythonProject7
pip install -r requirements.txt
```

**Key packages installed:**
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `torch`, `torchvision` - Deep learning
- `scikit-learn` - Machine learning
- `pydantic` - Data validation
- `python-multipart` - File upload support

### Step 2: Train Yield Prediction Model

If `models/yield_model.pkl` doesn't exist, train the yield model:

```bash
python train_yield_model.py
```

This will:
- Generate synthetic training data (or load from `yield_data.csv` if available)
- Train a Linear Regression model
- Save the model to `models/yield_model.pkl`
- Display performance metrics

**Optional:** To use real data, create a CSV file named `yield_data.csv` with columns:
```
nitrogen,phosphorus,potassium,ph,rainfall,yield
100,50,40,7.0,1000,5000
150,75,60,6.5,1200,6000
```

### Step 3: Verify Soil Model

Ensure `checkpoints/best_model.pth` exists. This should be your pre-trained CNN model.

If not present, train it using:
```bash
python train.py
```

---

## 🏃 Running the Server

Start the FastAPI server:

```bash
uvicorn main:app --reload --port 8000
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete

==================================================
AgriPredict Backend Starting...
==================================================

✓ Soil classification model loaded successfully
✓ Yield prediction model loaded successfully

==================================================
Server Ready! 🚀
API Docs: http://localhost:8000/docs
==================================================
```

### Server Options

- **`--reload`**: Auto-reload on code changes (development only)
- **`--port 8000`**: Run on port 8000 (default)
- **`--host 0.0.0.0`**: Accept connections from any IP
- **`--workers 4`**: Run with multiple workers (production)

### Production Deployment

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## 📡 API Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

Check if the server and models are running.

**Response:**
```json
{
  "status": "healthy",
  "soil_classifier_loaded": true,
  "yield_predictor_loaded": true
}
```

---

### 2. Soil Type Prediction

**Endpoint:** `POST /predict-soil`

Upload a soil image and get the predicted soil type.

**Request:**
```bash
curl -X POST http://localhost:8000/predict-soil \
  -F "file=@path/to/soil_image.jpg"
```

**Response:**
```json
{
  "success": true,
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
```

---

### 3. Yield Prediction (Single)

**Endpoint:** `POST /predict-yield`

Predict crop yield from soil parameters.

**Request:**
```bash
curl -X POST http://localhost:8000/predict-yield \
  -F "nitrogen=100" \
  -F "phosphorus=50" \
  -F "potassium=40" \
  -F "ph=7.0" \
  -F "rainfall=1000" \
  -F "temperature=25" \
  -F "humidity=65"
```

**Response:**
```json
{
  "success": true,
  "predicted_yield": 5242.5,
  "yield_unit": "kg/ha",
  "parameters": {
    "nitrogen": 100.0,
    "phosphorus": 50.0,
    "potassium": 40.0,
    "ph": 7.0,
    "rainfall": 1000.0,
    "temperature": 25.0,
    "humidity": 65.0
  },
  "model_version": "1.0"
}
```

---

### 4. Yield Prediction (Batch from CSV)

**Endpoint:** `POST /predict-yield-batch`

Upload a CSV file with multiple soil samples for batch prediction.

**CSV Format:**
```csv
nitrogen,phosphorus,potassium,ph,rainfall,temperature,humidity
100,50,40,7.0,1000,25,65
150,75,60,6.5,1200,26,70
120,60,50,7.5,1100,24,60
```

**Request:**
```bash
curl -X POST http://localhost:8000/predict-yield-batch \
  -F "file=@predictions.csv"
```

**Response:**
```json
{
  "success": true,
  "total_rows": 3,
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
      }
    },
    {
      "row": 2,
      "status": "success",
      "predicted_yield": 6150.0,
      "parameters": { ... }
    }
  ]
}
```

---

### 5. Model Information

**Endpoint:** `GET /model-info`

Get details about the loaded models.

**Response:**
```json
{
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
    "loaded": true
  },
  "yield_predictor": {
    "name": "Linear Regression Yield Predictor",
    "input_features": ["nitrogen", "phosphorus", "potassium", "ph", "rainfall"],
    "optional_features": ["temperature", "humidity"],
    "loaded": true
  }
}
```

---

### 6. API Documentation

**Swagger UI:** http://localhost:8000/docs

**ReDoc:** http://localhost:8000/redoc

Browse and test all endpoints interactively!

---

## 🔗 Integration with React

### Step 1: Copy the Custom Hook

Copy `react_api_client.js` to your React project:

```bash
# In agripredict folder
cp ../PythonProject7/react_api_client.js src/hooks/usePrediction.js
```

Convert to TypeScript if using `.tsx`:

```bash
# Rename and add TypeScript
mv src/hooks/usePrediction.js src/hooks/usePrediction.ts
```

### Step 2: Use in React Components

```tsx
import { usePrediction } from '@/hooks/usePrediction';

export function YourComponent() {
  const { predictSoil, predictYield, loading, error } = usePrediction();

  const handleSoilPrediction = async (imageFile: File) => {
    try {
      const result = await predictSoil(imageFile);
      console.log('Soil type:', result.soil_type);
      console.log('Confidence:', result.confidence);
    } catch (err) {
      console.error('Prediction failed:', err);
    }
  };

  const handleYieldPrediction = async () => {
    try {
      const result = await predictYield({
        nitrogen: 100,
        phosphorus: 50,
        potassium: 40,
        ph: 7.0,
        rainfall: 1000,
      });
      console.log('Predicted yield:', result.predicted_yield);
    } catch (err) {
      console.error('Prediction failed:', err);
    }
  };

  return (
    // Your component JSX
  );
}
```

### Step 3: Copy Example Components (Optional)

Copy the provided example components:

```bash
cp ../PythonProject7/SoilPredictionComponent.tsx src/components/AgriCare/
cp ../PythonProject7/YieldPredictionComponent.tsx src/components/AgriCare/
```

Then import and use them:

```tsx
import SoilPredictionComponent from '@/components/AgriCare/SoilPredictionComponent';
import YieldPredictionComponent from '@/components/AgriCare/YieldPredictionComponent';

export default function PredictionPage() {
  return (
    <div>
      <SoilPredictionComponent />
      <YieldPredictionComponent />
    </div>
  );
}
```

### Step 4: Configure CORS (if needed)

The API is already configured to accept requests from React dev servers (`localhost:5173`, `localhost:3000`) and any origin (`*` for development).

For production, update `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Production domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📚 Example Usage

### Python Client Example

```bash
python client_example.py
```

This demonstrates:
- Health check
- Soil prediction from an image
- Yield prediction with parameters
- Batch prediction from CSV

### React Component Example

See `SoilPredictionComponent.tsx` and `YieldPredictionComponent.tsx` for complete working examples with:
- File upload handling
- Form validation
- Error handling
- Loading states
- Results display
- Probability distribution visualization

### cURL Examples

**Predict soil type:**
```bash
curl -X POST http://localhost:8000/predict-soil \
  -F "file=@soil_image.jpg"
```

**Predict yield:**
```bash
curl -X POST http://localhost:8000/predict-yield \
  -F "nitrogen=100" \
  -F "phosphorus=50" \
  -F "potassium=40" \
  -F "ph=7.0" \
  -F "rainfall=1000"
```

**Check health:**
```bash
curl http://localhost:8000/health
```

---

## 🔧 Troubleshooting

### 1. "ModuleNotFoundError" when running the server

**Solution:** Install missing dependencies
```bash
pip install -r requirements.txt
```

### 2. "CUDA out of memory" error

**Solutions:**
- Clear GPU memory: Restart Python
- Use CPU instead: The app automatically falls back to CPU if GPU is unavailable
- Process smaller images

### 3. "Model not found at checkpoints/best_model.pth"

**Solution:** Train the soil classifier
```bash
python train.py
```

### 4. "Yield prediction model not loaded"

**Solution:** Train the yield model
```bash
python train_yield_model.py
```

### 5. React can't connect to API

**Check:**
- Backend is running: `http://localhost:8000/health`
- Port 8000 is not blocked by firewall
- React is using correct API URL: `http://localhost:8000`
- CORS is enabled (it is by default)

### 6. Slow predictions

**Solutions:**
- Use GPU (install CUDA): Predictions will be 10-100x faster
- Reduce image size in preprocessing
- Run with multiple workers: `uvicorn main:app --workers 4`

---

## 📈 Performance Notes

### Inference Times (approximate)

| Task | CPU | GPU |
|------|-----|-----|
| Soil classification | 100-500ms | 10-50ms |
| Yield prediction | <1ms | <1ms |

### Memory Usage

- Soil classifier: ~200MB RAM
- Yield predictor: ~10MB RAM
- Total: ~250MB

---

## 🔒 Security Considerations

1. **File uploads:** Only accept image files (`.jpg`, `.png`)
2. **Input validation:** All inputs are validated with Pydantic
3. **Error messages:** Generic error messages for production
4. **CORS:** Restrict origins in production

For production deployment:

```python
# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],  # Specific domain
    allow_methods=["POST", "GET"],              # Only needed methods
    allow_headers=["Content-Type"],
)
```

---

## 🚀 Production Deployment

### Using Gunicorn + Uvicorn

```bash
pip install gunicorn

gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
```

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:
```bash
docker build -t agripredict-backend .
docker run -p 8000:8000 agripredict-backend
```

---

## 📝 API Response Format

All successful responses follow this format:

```json
{
  "success": true,
  "data": { ... }
}
```

Error responses:

```json
{
  "success": false,
  "error": "Error message describing what went wrong"
}
```

---

## 🤝 Contributing

To add new endpoints:

1. Create a new function in `main.py`
2. Define request/response schemas in `schemas.py`
3. Document the endpoint with docstrings
4. Test with `/docs` endpoint

Example:

```python
@app.post("/new-endpoint", response_model=NewResponse)
async def new_endpoint(param: str):
    """Endpoint description"""
    # Implementation
    return NewResponse(...)
```

---

## 📞 Support

For issues:
1. Check `/docs` endpoint for API documentation
2. Review error messages in server logs
3. Check `troubleshooting` section above
4. Verify dependencies are installed: `pip list`

---

## 📄 License

This project is part of the AgriPredict application.

---

## 🎉 Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Train yield model: `python train_yield_model.py`
3. ✅ Start server: `uvicorn main:app --reload --port 8000`
4. ✅ Visit `http://localhost:8000/docs` for interactive API testing
5. ✅ Integrate with React using `react_api_client.js`
6. ✅ Deploy to production when ready

**Happy farming! 🌾**
