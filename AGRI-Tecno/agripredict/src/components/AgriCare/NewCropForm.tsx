import { useState } from "react";
import { MapPin, Calendar, RotateCcw, Sparkles } from "lucide-react";
import ImageUploader from "./ImageUploader";

interface NewCropFormProps {
  onSubmit: (data: NewCropFormData) => void;
  onReset: () => void;
  isLoading: boolean;
}

interface NewCropFormData {
  crop: string;
  district: string;
  block: string;
  latitude: string;
  longitude: string;
  farmSize: string;
  sowingDate: string;
  irrigationType: string;
  previousCrop: string;
  lastCultivationDate: string;
  variety: string;
  soilImage?: File;
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

const NewCropForm = ({ onSubmit, onReset, isLoading }: NewCropFormProps) => {
  const [formData, setFormData] = useState<NewCropFormData>({
    crop: "",
    district: "",
    block: "",
    latitude: "",
    longitude: "",
    farmSize: "",
    sowingDate: "",
    irrigationType: "",
    previousCrop: "",
    lastCultivationDate: "",
    variety: "",
    soilImage: undefined,
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
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
      sowingDate: "",
      irrigationType: "",
      previousCrop: "",
      lastCultivationDate: "",
      variety: "",
      soilImage: undefined,
    });
    onReset();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Crop Selection */}
      <div>
        <label htmlFor="cropSelect" className="agri-label">
          Select Crop
        </label>
        <select
          id="cropSelect"
          name="crop"
          value={formData.crop}
          onChange={handleChange}
          className="agri-select"
          required
          aria-required="true"
        >
          <option value="">Choose a crop</option>
          {ODISHA_CROPS.map((crop) => (
            <option key={crop} value={crop}>
              {crop}
            </option>
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
            value={
              formData.latitude && formData.longitude
                ? `${formData.latitude}, ${formData.longitude}`
                : ""
            }
          />
          <button
            type="button"
            id="locationGpsBtn"
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
          <label htmlFor="district" className="agri-label">
            District
          </label>
          <input
            type="text"
            id="district"
            name="district"
            value={formData.district}
            onChange={handleChange}
            placeholder="e.g., Khordha"
            className="agri-input"
          />
        </div>
        <div>
          <label htmlFor="block" className="agri-label">
            Block
          </label>
          <input
            type="text"
            id="block"
            name="block"
            value={formData.block}
            onChange={handleChange}
            placeholder="e.g., Balianta"
            className="agri-input"
          />
        </div>
      </div>

      {/* Hidden lat/lng inputs */}
      <input
        type="hidden"
        id="latitude"
        name="latitude"
        value={formData.latitude}
      />
      <input
        type="hidden"
        id="longitude"
        name="longitude"
        value={formData.longitude}
      />

      {/* Farm Size */}
      <div>
        <label htmlFor="farmSize" className="agri-label">
          Farm Size (acres)
        </label>
        <input
          type="number"
          id="farmSize"
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

      {/* Sowing Date */}
      <div>
        <label htmlFor="sowingDate" className="agri-label">
          Sowing Date
        </label>
        <div className="relative">
          <input
            type="date"
            id="sowingDate"
            name="sowingDate"
            value={formData.sowingDate}
            onChange={handleChange}
            className="agri-input"
            required
            aria-required="true"
          />
          <Calendar className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
        </div>
      </div>

      {/* Irrigation Type */}
      <div>
        <label htmlFor="irrigationType" className="agri-label">
          Irrigation Type
        </label>
        <select
          id="irrigationType"
          name="irrigationType"
          value={formData.irrigationType}
          onChange={handleChange}
          className="agri-select"
          required
          aria-required="true"
        >
          <option value="">Choose irrigation method</option>
          {IRRIGATION_TYPES.map((type) => (
            <option key={type} value={type}>
              {type}
            </option>
          ))}
        </select>
      </div>

      {/* Previously Grown Crop */}
      <div>
        <label htmlFor="previousCrop" className="agri-label">
          Previously Grown Crop
        </label>
        <input
          type="text"
          id="previousCrop"
          name="previousCrop"
          value={formData.previousCrop}
          onChange={handleChange}
          placeholder="e.g., Wheat"
          className="agri-input"
        />
      </div>

      {/* Last Cultivation Date */}
      <div>
        <label htmlFor="lastCultivationDate" className="agri-label">
          Last Cultivation Date (Previous crop harvest date)
        </label>
        <div className="relative">
          <input
            type="date"
            id="lastCultivationDate"
            name="lastCultivationDate"
            value={formData.lastCultivationDate}
            onChange={handleChange}
            className="agri-input"
          />
          <Calendar className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
        </div>
      </div>

      {/* Variety (Optional) */}
      <div>
        <label htmlFor="varietySelect" className="agri-label">
          Variety{" "}
          <span className="text-muted-foreground font-normal">(Optional)</span>
        </label>
        <input
          type="text"
          id="varietySelect"
          name="variety"
          value={formData.variety}
          onChange={handleChange}
          placeholder="e.g., IR64, Swarna"
          className="agri-input"
        />
      </div>

      {/* Soil Image Upload (Optional) */}
      <ImageUploader
        id="newCropUIImagesPlaceholder"
        label="Upload Soil Image (Optional)"
        placeholder="Upload a clear photo of your soil from camera or gallery - helps improve accuracy"
        multiple={false}
        onImagesChange={(images) => {
          setFormData({
            ...formData,
            soilImage: images.length > 0 ? images[0] : undefined,
          });
        }}
      />

      {/* Action Buttons */}
      <div className="flex gap-3 pt-4">
        <button
          type="submit"
          id="predictNewBtn"
          disabled={isLoading}
          className="agri-btn-primary flex-1 flex items-center justify-center gap-2"
          aria-label="Predict and recommend"
        >
          <Sparkles className="w-5 h-5" />
          {isLoading ? "Processing..." : "Predict & Recommend"}
        </button>
        <button
          type="button"
          id="resetNewBtn"
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

export default NewCropForm;
