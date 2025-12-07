"""
React API Client Hook
====================

This is a custom React hook for calling the FastAPI backend.
Place this in your React project's hooks directory.

Usage in React components:
    import { usePrediction } from './hooks/usePrediction';
    
    const { predictSoil, predictYield, loading, error } = usePrediction();
    
    const result = await predictSoil(imageFile);
"""

import { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

export const usePrediction = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  /**
   * Predict soil type from an image
   * @param {File} imageFile - Image file from input
   * @returns {Promise} Prediction result
   */
  const predictSoil = async (imageFile) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', imageFile);

      const response = await fetch(`${API_BASE_URL}/predict-soil`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to predict soil');
      }

      const data = await response.json();
      setLoading(false);
      return data;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  };

  /**
   * Predict crop yield from soil parameters
   * @param {Object} parameters - Soil parameters
   * @returns {Promise} Prediction result
   */
  // New: Predict yield from a location (lat, lon). Optionally pass weatherApiKey.
  const predictYield = async ({ lat, lon, weatherApiKey = null }) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('lat', lat);
      formData.append('lon', lon);
      if (weatherApiKey) formData.append('weather_api_key', weatherApiKey);

      const response = await fetch(`${API_BASE_URL}/predict-yield`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to predict yield');
      }

      const data = await response.json();
      setLoading(false);
      return data;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  };

  /**
   * Predict yield for multiple samples from CSV
   * @param {File} csvFile - CSV file with soil parameters
   * @returns {Promise} Batch prediction result
   */
  const predictYieldBatch = async (csvFile) => {
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', csvFile);

      const response = await fetch(`${API_BASE_URL}/predict-yield-batch`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'Failed to process CSV');
      }

      const data = await response.json();
      setLoading(false);
      return data;
    } catch (err) {
      setError(err.message);
      setLoading(false);
      throw err;
    }
  };

  /**
   * Check API health status
   * @returns {Promise} Health check result
   */
  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error('API unhealthy');
      return await response.json();
    } catch (err) {
      console.error('API health check failed:', err);
      return { status: 'error' };
    }
  };

  /**
   * Get model information
   * @returns {Promise} Model info
   */
  const getModelInfo = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/model-info`);
      if (!response.ok) throw new Error('Failed to get model info');
      return await response.json();
    } catch (err) {
      console.error('Failed to get model info:', err);
      return null;
    }
  };

  return {
    predictSoil,
    predictYield,
    predictYieldBatch,
    checkHealth,
    getModelInfo,
    loading,
    error,
    setError,
  };
};

export default usePrediction;
