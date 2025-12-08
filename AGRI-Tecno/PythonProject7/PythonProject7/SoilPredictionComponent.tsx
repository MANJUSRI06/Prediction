/*
Example React Component for Soil Prediction
------------------------------------------

This is a complete example React component that uses the API to predict soil type.
Place this file in: `agripredict/src/components/AgriCare/SoilPredictionComponent.tsx`

It demonstrates:
- File upload handling
- API integration using the custom hook
- Loading states
- Error handling
- Display of results
*/

import React, { useState } from 'react';
import usePrediction from '../../hooks/usePrediction';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Loader2, Upload, CheckCircle, AlertTriangle } from 'lucide-react';

interface SoilPredictionResult {
  success: boolean;
  soil_type: string;
  confidence: number;
  class_index: number;
  all_probabilities: Record<string, number>;
}

const SoilPredictionComponent: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>('');
  const [prediction, setPrediction] = useState<SoilPredictionResult | null>(null);
  const { predictSoil, loading, error, setError } = usePrediction();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!['image/jpeg', 'image/png', 'image/jpg'].includes(file.type)) {
        setError('Please upload a JPG or PNG image');
        return;
      }

      // Validate file size (max 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('Image size must be less than 10MB');
        return;
      }

      setSelectedFile(file);
      setError(null);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handlePredict = async () => {
    if (!selectedFile) {
      setError('Please select an image');
      return;
    }

    try {
      const result = await predictSoil(selectedFile);
      setPrediction(result);
      setError(null);
    } catch (err) {
      console.error('Prediction error:', err);
      // Surface error message in UI via hook state
      const msg = (err as any)?.message || 'Prediction failed';
      setError(msg);
      setPrediction(null);
    }
  };

  const soilDescriptions: Record<string, string> = {
    'Alluvial Soil': 'Fertile soil found in river plains, ideal for wheat and rice.',
    'Arid Soil': 'Sandy, dry soil found in deserts, requires irrigation.',
    'Black Soil': 'Rich in minerals and organic matter, retains moisture well.',
    'Laterite Soil': 'Reddish soil, acidic, found in tropical regions.',
    'Mountain Soil': 'Thin, rocky soil found in mountainous terrain.',
    'Red Soil': 'Iron-rich, acidic soil found in tropical regions.',
    'Yellow Soil': 'Less fertile, found in subtropical regions.',
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-4 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>🌱 Soil Type Prediction</CardTitle>
          <CardDescription>
            Upload a soil image to classify its type using AI
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* File Upload */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition">
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
              id="file-input"
            />
            <label htmlFor="file-input" className="cursor-pointer">
              <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
              <p className="text-sm text-gray-600">
                Click to upload or drag and drop
              </p>
              <p className="text-xs text-gray-500">PNG or JPG (max. 10MB)</p>
            </label>
          </div>

          {/* Preview */}
          {preview && (
            <div className="relative rounded-lg overflow-hidden bg-gray-100">
              <img
                src={preview}
                alt="Selected soil image"
                className="w-full h-64 object-cover"
              />
            </div>
          )}

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Predict Button */}
          <Button
            onClick={handlePredict}
            disabled={!selectedFile || loading}
            className="w-full"
            size="lg"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing...
              </>
            ) : (
              'Predict Soil Type'
            )}
          </Button>

          {/* Results */}
          {prediction && (
            <div className="space-y-4">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span className="font-semibold text-green-900">
                    Prediction Complete
                  </span>
                </div>

                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-600">Soil Type</p>
                    <p className="text-2xl font-bold text-green-700">
                      {prediction.soil_type}
                    </p>
                  </div>

                  <div>
                    <p className="text-sm text-gray-600">Confidence Score</p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-green-600 h-2 rounded-full transition-all"
                          style={{
                            width: `${prediction.confidence * 100}%`,
                          }}
                        />
                      </div>
                      <span className="font-semibold text-gray-700">
                        {(prediction.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-600 mb-2">Description</p>
                    <p className="text-gray-700">
                      {soilDescriptions[prediction.soil_type] ||
                        'No description available'}
                    </p>
                  </div>

                  {/* Probability Distribution */}
                  <div>
                    <p className="text-sm text-gray-600 mb-2">All Predictions</p>
                    <div className="space-y-2">
                      {Object.entries(prediction.all_probabilities)
                        .sort(([, a], [, b]) => b - a)
                        .map(([soilType, prob]) => (
                          <div
                            key={soilType}
                            className="flex items-center justify-between"
                          >
                            <span className="text-sm text-gray-700">
                              {soilType}
                            </span>
                            <div className="flex items-center gap-2">
                              <div className="w-24 bg-gray-200 rounded-full h-1.5">
                                <div
                                  className="bg-blue-500 h-1.5 rounded-full"
                                  style={{ width: `${prob * 100}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-600 w-10">
                                {(prob * 100).toFixed(1)}%
                              </span>
                            </div>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SoilPredictionComponent;
