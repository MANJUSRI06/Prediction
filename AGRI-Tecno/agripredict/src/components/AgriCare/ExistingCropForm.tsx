import { useState } from "react";
import { MapPin, Calendar, RotateCcw, Stethoscope } from "lucide-react";
import ImageUploader from "./ImageUploader";

interface ExistingCropFormProps {
  onSubmit: (data: ExistingCropFormData) => void;
  onReset: () => void;
  isLoading: boolean;
}

export interface ExistingCropFormData {
  crop: string;
  district: string;
  block: string;
  latitude: string;
  longitude: string;
  farmSize: string;
  sowDate: string;
  todayDate: string;
  irrigationType: string;
  plantPhotos: File[];
  managementNotes: string;
}

const ODISHA_CROPS = [
  "Rice",
  "Maize",
  "Groundnut",
  "Pulses",
  "Vegetables",
  "Cotton",
  "Sugarcane",
];

const IRRIGATION_TYPES = [
  "Rainfed",
  "Drip",
  "Sprinkler",
  "Canal",
  "Groundwater",
];

const ExistingCropForm = ({ onSubmit, onReset, isLoading }: ExistingCropFormProps) => {
  const [formData, setFormData] = useState<ExistingCropFormData>({
    crop: "",
    district: "",
    block: "",
    latitude: "",
    longitude: "",
    farmSize: "",
    sowDate: "",
    todayDate: new Date().toISOString().split("T")[0],
    irrigationType: "",
    plantPhotos: [],
    managementNotes: "",
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleGpsClick = () => {
    // TODO: Replace with actual geolocation API call
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setFormData({
            ...formData,
            latitude: position.coords.latitude.toFixed(6),
            longitude: position.coords.longitude.toFixed(6),
          });
        },
        (error) => {
          console.error("GPS Error:", error);
          // Fallback demo coordinates
          setFormData({
            ...formData,
            latitude: "20.2961",
            longitude: "85.8245",
            district: "Khordha",
            block: "Balianta",
          });
        }
      );
    }
  };

  const handleImagesChange = (images: File[]) => {
    setFormData({ ...formData, plantPhotos: images });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const handleReset = () => {
    setFormData({
      crop: "",
      district: "",
      block: "",
      latitude: "",
      longitude: "",
      farmSize: "",
      sowDate: "",
      todayDate: new Date().toISOString().split("T")[0],
      irrigationType: "",
      plantPhotos: [],
      managementNotes: "",
    });
    onReset();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Crop Selection */}
      <div>
        <label htmlFor="cropSelectExisting" className="agri-label">
          Select Crop
        </label>
        <select
          id="cropSelectExisting"
          name="crop"
          value={formData.crop}
          onChange={handleChange}
          className="agri-select"
          required
          aria-required="true"
        >
          <option value="">Choose a crop</option>
          {ODISHA_CROPS.map((crop) => (
            <option key={crop} value={crop}>{crop}</option>
          ))}
        </select>
      </div>

      {/* Location with GPS */}
      <div>
        <label className="agri-label">Location</label>
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="Enter Location"
            className="agri-input flex-1"
            readOnly
            value={formData.latitude && formData.longitude 
              ? `${formData.latitude}, ${formData.longitude}` 
              : ""}
          />
          <button
            type="button"
            id="locationGpsBtnExisting"
            onClick={handleGpsClick}
            className="agri-btn-primary flex items-center gap-2 whitespace-nowrap"
            aria-label="Auto-detect GPS location"
          >
            <MapPin className="w-4 h-4" />
            GPS Auto-detect
          </button>
        </div>
      </div>

      {/* District and Block */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label htmlFor="districtExisting" className="agri-label">District</label>
          <input
            type="text"
            id="districtExisting"
            name="district"
            value={formData.district}
            onChange={handleChange}
            placeholder="e.g., Khordha"
            className="agri-input"
          />
        </div>
        <div>
          <label htmlFor="blockExisting" className="agri-label">Block</label>
          <input
            type="text"
            id="blockExisting"
            name="block"
            value={formData.block}
            onChange={handleChange}
            placeholder="e.g., Balianta"
            className="agri-input"
          />
        </div>
      </div>

      {/* Hidden lat/lng inputs */}
      <input type="hidden" id="latitudeExisting" name="latitude" value={formData.latitude} />
      <input type="hidden" id="longitudeExisting" name="longitude" value={formData.longitude} />

      {/* Farm Size */}
      <div>
        <label htmlFor="farmSizeExisting" className="agri-label">Farm Size (acres)</label>
        <input
          type="number"
          id="farmSizeExisting"
          name="farmSize"
          value={formData.farmSize}
          onChange={handleChange}
          placeholder="e.g., 5.5"
          min="0"
          step="0.1"
          className="agri-input"
          required
          aria-required="true"
        />
      </div>

      {/* Sow Date */}
      <div>
        <label htmlFor="sowDateExisting" className="agri-label">Crop Started Date (Sowed)</label>
        <div className="relative">
          <input
            type="date"
            id="sowDateExisting"
            name="sowDate"
            value={formData.sowDate}
            onChange={handleChange}
            className="agri-input"
            required
            aria-required="true"
          />
          <Calendar className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
        </div>
      </div>

      {/* Today's Date (Auto-filled) */}
      <div>
        <label htmlFor="todayDate" className="agri-label">Today's Date</label>
        <input
          type="date"
          id="todayDate"
          name="todayDate"
          value={formData.todayDate}
          className="agri-input bg-muted/50"
          readOnly
          aria-readonly="true"
        />
      </div>

      {/* Irrigation Type */}
      <div>
        <label htmlFor="irrigationTypeExisting" className="agri-label">Irrigation Type</label>
        <select
          id="irrigationTypeExisting"
          name="irrigationType"
          value={formData.irrigationType}
          onChange={handleChange}
          className="agri-select"
          required
          aria-required="true"
        >
          <option value="">Choose irrigation method</option>
          {IRRIGATION_TYPES.map((type) => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      {/* Plant Photo Upload */}
      <ImageUploader
        id="plantPhoto"
        label="Plant Photo Upload"
        placeholder="Upload plant images (camera preferred). Mark affected areas."
        multiple={true}
        onImagesChange={handleImagesChange}
      />

      {/* Management Notes */}
      <div>
        <label htmlFor="managementNotes" className="agri-label">
          Farmer Observations / Management Notes
        </label>
        <textarea
          id="managementNotes"
          name="managementNotes"
          value={formData.managementNotes}
          onChange={handleChange}
          placeholder="Describe any symptoms, issues, or observations about your crop..."
          rows={4}
          className="agri-input resize-none"
        />
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          id="submitExistingBtn"
          disabled={isLoading}
          className="agri-btn-primary flex-1 flex items-center justify-center gap-2"
          aria-label="Diagnose and recommend"
        >
          <Stethoscope className="w-5 h-5" />
          {isLoading ? "Analyzing..." : "Diagnose & Recommend"}
        </button>
        <button
          type="button"
          onClick={handleReset}
          className="agri-btn-outline flex items-center gap-2"
          aria-label="Reset form"
        >
          <RotateCcw className="w-4 h-4" />
          Reset
        </button>
      </div>
    </form>
  );
};

export default ExistingCropForm;
