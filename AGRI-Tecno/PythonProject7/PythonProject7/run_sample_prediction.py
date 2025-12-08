"""Run a sample yield prediction locally without starting the HTTP server.

This script fetches SoilGrids and optional weather (using provided key),
builds parameters, loads the yield predictor (or its dummy), and prints
the prediction result as JSON to stdout.

Usage:
    python run_sample_prediction.py
"""

import json
import requests
from ml_models import YieldPredictor

def fetch_soilgrids(lat, lon):
    url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lat={lat}&lon={lon}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()


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
            try:
                return float(sum(vals) / len(vals))
            except Exception:
                return None
    try:
        return float(val)
    except Exception:
        return None


def main():
    lat = 20.2961
    lon = 85.8245
    weather_api_key = "7c355fbc1e7349210b0cca55b1a61def"  # optional

    soil_props = {}
    try:
        sg = fetch_soilgrids(lat, lon)
        props = sg.get("properties", {})
        n_val = deep_find(props, ["nitrogen", "n"])  # may be dict with 'values'
        ph_val = deep_find(props, ["phh2o", "ph"])   # pH
        n_num = numeric_from(n_val)
        ph_num = numeric_from(ph_val)
        if n_num is not None:
            soil_props["nitrogen"] = float(n_num)
        if ph_num is not None:
            soil_props["ph"] = float(ph_num)
    except Exception as e:
        print("Warning: SoilGrids fetch failed:", e)

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
            print("Warning: weather fetch failed:", e)

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
    if parameters.get("rainfall") == 1000.0 and weather.get("recent_rain_mm"):
        parameters["rainfall"] = max(200.0, min(2000.0, weather.get("recent_rain_mm", 0.0) * 365))

    predictor = YieldPredictor()
    result = predictor.predict(parameters)

    output = {
        "parameters": parameters,
        "prediction": result,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
