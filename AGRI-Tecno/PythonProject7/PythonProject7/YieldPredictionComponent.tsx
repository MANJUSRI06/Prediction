/*
Example React Component for Yield Prediction
-------------------------------------------

This is a complete example React component that uses the API to predict crop yield.
Place this file in: `agripredict/src/components/AgriCare/YieldPredictionComponent.tsx`

It demonstrates:
- Form handling with location inputs (lat/lon)
- API integration
- CSV file upload for batch predictions
- Results display
- Error handling
*/

import React, { useState } from 'react';
import usePrediction from '../../hooks/usePrediction';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Upload, CheckCircle, AlertTriangle } from 'lucide-react';

interface YieldPredictionResult {
  success: boolean;
  predicted_yield: number;
  yield_unit: string;
  parameters: Record<string, number>;
  model_version: string;
}

interface BatchResult {
  row: number;
  status: string;
  predicted_yield?: number;
  error?: string;
}

const YieldPredictionComponent: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'single' | 'batch'>('single');
  const [formData, setFormData] = useState({
    lat: '',
    lon: '',
    weatherApiKey: '',
  });
  const [prediction, setPrediction] = useState<YieldPredictionResult | null>(null);
  const [batchFile, setBatchFile] = useState<File | null>(null);
  const [batchResults, setBatchResults] = useState<BatchResult[] | null>(null);
  
  const { predictYield, predictYieldBatch, loading, error, setError } = usePrediction();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handlePredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validate lat/lon
    if (!formData.lat || !formData.lon) {
      setError('Please provide latitude and longitude');
      return;
    }

    try {
      const lat = parseFloat(formData.lat);
      const lon = parseFloat(formData.lon);
      const weatherApiKey = formData.weatherApiKey || undefined;

      const result = await predictYield({ lat, lon, weatherApiKey });
      setPrediction(result);
    } catch (err) {
      console.error('Prediction error:', err);
    }
  };

  const handleBatchFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.type !== 'text/csv') {
        setError('Please upload a CSV file');
        return;
      }
      setBatchFile(file);
      setError(null);
    }
  };

  const handleBatchPredict = async () => {
    if (!batchFile) {
      setError('Please select a CSV file');
      return;
    }

    try {
      const result = await predictYieldBatch(batchFile);
      setBatchResults(result.predictions);
    } catch (err) {
      console.error('Batch prediction error:', err);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-4 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>🌾 Crop Yield Prediction</CardTitle>
          <CardDescription>
            Predict crop yield based on soil parameters
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Tab Navigation */}
          <div className="flex gap-2 border-b">
            <button
              onClick={() => setActiveTab('single')}
              className={`px-4 py-2 font-medium border-b-2 transition ${
                activeTab === 'single'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Single Prediction
            </button>
            <button
              onClick={() => setActiveTab('batch')}
              className={`px-4 py-2 font-medium border-b-2 transition ${
                activeTab === 'batch'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Batch Predictions (CSV)
            </button>
          </div>

          {/* Error Alert */}
          {error && (
            <Alert variant="destructive">
              <AlertTriangle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          {/* Single Prediction Tab */}
          {activeTab === 'single' && (
            <form onSubmit={handlePredict} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Latitude */}
                <div className="space-y-2">
                  <Label htmlFor="lat">
                    Latitude <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="lat"
                    name="lat"
                    type="number"
                    placeholder="e.g., 20.2961"
                    value={formData.lat}
                    onChange={handleInputChange}
                    step="0.0001"
                    required
                  />
                </div>

                {/* Longitude */}
                <div className="space-y-2">
                  <Label htmlFor="lon">
                    Longitude <span className="text-red-500">*</span>
                  </Label>
                  <Input
                    id="lon"
                    name="lon"
                    type="number"
                    placeholder="e.g., 85.8245"
                    value={formData.lon}
                    onChange={handleInputChange}
                    step="0.0001"
                    required
                  />
                </div>

                {/* Weather API Key (Optional) */}
                <div className="space-y-2 md:col-span-2">
                  <Label htmlFor="weatherApiKey">Weather API Key (Optional)</Label>
                  <Input
                    id="weatherApiKey"
                    name="weatherApiKey"
                    type="text"
                    placeholder="OpenWeatherMap API key"
                    value={formData.weatherApiKey}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <Button
                type="submit"
                disabled={loading}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Predicting...
                  </>
                ) : (
                  'Predict Yield'
                )}
              </Button>

              {/* Prediction Result */}
              {prediction && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 space-y-3">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-5 w-5 text-blue-600" />
                    <span className="font-semibold text-blue-900">
                      Prediction Complete
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Predicted Yield</p>
                    <p className="text-3xl font-bold text-blue-700">
                      {prediction.predicted_yield.toFixed(2)}
                    </p>
                    <p className="text-sm text-gray-600">
                      {prediction.yield_unit}
                    </p>
                  </div>
                </div>
              )}
            </form>
          )}

          {/* Batch Prediction Tab */}
          {activeTab === 'batch' && (
            <div className="space-y-4">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-500 transition">
                <input
                  type="file"
                  accept=".csv"
                  onChange={handleBatchFileChange}
                  className="hidden"
                  id="csv-input"
                />
                <label htmlFor="csv-input" className="cursor-pointer">
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                  <p className="text-sm text-gray-600">
                    Click to upload or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">
                    CSV with columns: nitrogen, phosphorus, potassium, ph, rainfall
                  </p>
                </label>
              </div>

              {batchFile && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <p className="text-sm font-medium text-gray-700">
                    Selected: {batchFile.name}
                  </p>
                </div>
              )}

              <Button
                onClick={handleBatchPredict}
                disabled={!batchFile || loading}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  'Process Batch'
                )}
              </Button>

              {/* Batch Results */}
              {batchResults && (
                <div className="space-y-2">
                  <h3 className="font-semibold text-gray-900">
                    Results ({batchResults.length} rows)
                  </h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b">
                          <th className="px-4 py-2 text-left">Row</th>
                          <th className="px-4 py-2 text-left">Status</th>
                          <th className="px-4 py-2 text-right">Yield (kg/ha)</th>
                        </tr>
                      </thead>
                      <tbody>
                        {batchResults.map((result, idx) => (
                          <tr key={idx} className="border-b">
                            <td className="px-4 py-2">{result.row}</td>
                            <td className="px-4 py-2">
                              {result.status === 'success' ? (
                                <span className="text-green-600 font-medium">✓ Success</span>
                              ) : (
                                <span className="text-red-600 font-medium">✗ Error</span>
                              )}
                            </td>
                            <td className="px-4 py-2 text-right font-semibold">
                              {result.status === 'success'
                                ? result.predicted_yield?.toFixed(2)
                                : result.error}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default YieldPredictionComponent;
