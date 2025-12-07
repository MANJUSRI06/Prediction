import { NewCropResultData } from "./NewCropResults";
import { ExistingCropResultData } from "./ExistingCropResults";

/**
 * Sample data for New Crop Prediction results
 * TODO: Replace with fetch('/api/predict/new', {...})
 * 
 * Expected Request Schema:
 * {
 *   crop: string,
 *   latitude: string,
 *   longitude: string,
 *   district: string,
 *   block: string,
 *   farmSize: number,
 *   sowingDate: string (ISO date),
 *   irrigationType: string,
 *   previousCrop: string,
 *   lastCultivationDate: string (ISO date),
 *   variety?: string
 * }
 * 
 * Expected Response Schema: NewCropResultData
 */
export const sampleNewResult: NewCropResultData = {
  predictedYieldPct: 78,
  predictedYieldQtyPerAcre: 18,
  totalYield: 90, // Will be calculated based on farm size
  weatherRecommendation: "Favorable conditions expected for the next 2 weeks. Monitor for sudden rainfall during flowering stage. Consider delayed sowing if monsoon onset is late.",
  weatherRisk: "medium",
  soilSuggestions: {
    nitrogen: { value: 65, status: "Optimal", suggestion: "Maintain current practices." },
    phosphorus: { value: 18, status: "Low", suggestion: "Apply 20 kg DAP per acre to boost growth." },
    potassium: { value: 120, status: "Optimal", suggestion: "Maintain current practices." },
    ph: { value: 6.5, status: "Good", suggestion: "Soil pH is ideal for most crops." },
  },
  irrigationSchedule: [
    { day: "Monday", amount: "15 mm", weather: "Clear, sunny" },
    { day: "Tuesday", amount: "20 mm", weather: "Moderate humidity" },
    { day: "Wednesday", amount: "Skip", weather: "Light rain expected", skip: true },
    { day: "Thursday", amount: "10 mm", weather: "Warm, dry" },
    { day: "Friday", amount: "15 mm", weather: "Sunny, breezy" },
  ],
  irrigationAlert: "Tuesday",
  fertilizerRecommendation: {
    ratio: "40:20:20",
    important: "Adjust application based on real-time weather and crop observation.",
    splits: [
      { stage: "Vegetative Growth", day: 10, fertilizer: "Urea: 20 kg/acre" },
      { stage: "Flowering Stage", day: 25, fertilizer: "DAP + MOP: 10 kg/acre each" },
      { stage: "Grain Filling", day: 45, fertilizer: "Urea: 15 kg/acre" },
    ],
  },
  growthStages: [
    { name: "Germination", days: "Days 1-7", current: false, icon: "🌱" },
    { name: "Vegetative Growth", days: "Days 8-30", current: true, icon: "🌿" },
    { name: "Flowering Stage", days: "Days 31-45", current: false, icon: "🌸" },
    { name: "Fruiting Stage", days: "Days 46-60", current: false, icon: "🍃" },
    { name: "Harvest", days: "Days 61-75", current: false, icon: "🌾" },
  ],
  pestRisks: [
    { name: "Stem Borer", level: "medium" },
    { name: "Leaf Blast", level: "low" },
    { name: "Brown Plant Hopper", level: "high" },
    { name: "Bacterial Blight", level: "low" },
  ],
  costProfit: {
    costPerAcre: 25000,
    revenuePerAcre: 45000,
    profitPerAcre: 20000,
  },
  seasonComparison: {
    changePercent: 12,
    trend: "up",
  },
  blockDiagramTasks: [
    { day: 1, title: "Land Prep", description: "Plowing and leveling", type: "sowing" },
    { day: 5, title: "Sowing", description: "Seed planting", type: "sowing" },
    { day: 10, title: "1st Irrigation", description: "Initial watering", type: "irrigation" },
    { day: 15, title: "Weeding", description: "Remove weeds", type: "growth" },
    { day: 20, title: "Fertilizer", description: "Apply NPK", type: "fertilizer" },
    { day: 30, title: "Pest Check", description: "Monitor pests", type: "pest" },
    { day: 45, title: "Flowering", description: "Flowering stage", type: "growth" },
    { day: 60, title: "Harvest Prep", description: "Final irrigation", type: "irrigation" },
    { day: 75, title: "Harvest", description: "Crop harvest", type: "harvest" },
  ],
};

/**
 * Sample data for Existing Crop Diagnosis results
 * TODO: Replace with fetch('/api/predict/existing', {...})
 * 
 * Expected Request Schema:
 * {
 *   crop: string,
 *   latitude: string,
 *   longitude: string,
 *   district: string,
 *   block: string,
 *   farmSize: number,
 *   sowDate: string (ISO date),
 *   todayDate: string (ISO date),
 *   irrigationType: string,
 *   plantPhotos: File[] (multipart/form-data),
 *   managementNotes: string
 * }
 * 
 * Expected Response Schema: ExistingCropResultData
 * 
 * Image Processing API Response Shape:
 * {
 *   issue: "leaf_blight" | "stem_borer" | "nitrogen_deficiency" | ...,
 *   confidence: 0.86,
 *   boxes: [{ x: 10, y: 20, width: 30, height: 25 }, ...]
 * }
 */
export const sampleExistingResult: ExistingCropResultData = {
  diagnosedIssue: "Nitrogen Deficiency + Early Leaf Blast (Fungal)",
  issueConfidence: 86,
  issueEvidence: {
    imageUrl: "/placeholder.svg", // Replace with actual uploaded image
    boundingBoxes: [
      { x: 20, y: 30, width: 25, height: 20 },
      { x: 55, y: 45, width: 20, height: 15 },
    ],
  },
  imageProcessingLog: "Detected: Yellowing patterns consistent with nitrogen stress (chlorosis) on lower leaves. Small brown lesions with gray centers indicative of early-stage leaf blast fungus. Leaf tip burn observed in 3 images.",
  soilTypeFromImage: "Loamy Soil",
  recommendedCropForSoil: ["Rice", "Maize", "Groundnut"],
  remedialActions: [
    "Day 1-2: Apply 25 kg Urea per acre to address nitrogen deficiency immediately.",
    "Day 1: Spray Tricyclazole 75% WP @ 0.6 g/L water for leaf blast control.",
    "Day 3: Ensure proper drainage to reduce fungal spread risk.",
    "Day 5: Apply potassium silicate foliar spray to strengthen plant immunity.",
    "Day 7: Re-inspect affected areas and repeat fungicide if needed.",
    "Week 2: Monitor new growth for symptoms recurrence.",
  ],
  irrigationAdjustments: [
    "Reduce irrigation by 20% for next 5 days to limit fungal spread.",
    "Shift to morning irrigation only (before 8 AM).",
    "Avoid overhead sprinkler; use drip or furrow irrigation.",
    "Resume normal schedule after fungal symptoms subside.",
  ],
  growthStageExisting: {
    currentStage: "Vegetative",
    daysToNextStage: 12,
    nextStage: "Flowering",
  },
  costAdjustmentEstimate: {
    unresolvedLoss: 8500,
    resolvedGain: 5000,
  },
  historyComparison: "Similar nitrogen deficiency was observed in Kharif 2023. Timely urea application resulted in 90% recovery. Current conditions are slightly more favorable due to better soil moisture.",
};

/**
 * Demo function to populate New Crop results
 * Call this to test UI without backend
 */
export const populateNewCropResults = (farmSize: number): NewCropResultData => {
  return {
    ...sampleNewResult,
    totalYield: Math.round(sampleNewResult.predictedYieldQtyPerAcre * farmSize),
  };
};

/**
 * Demo function to populate Existing Crop results
 * Call this to test UI without backend
 */
export const populateExistingCropResults = (): ExistingCropResultData => {
  return { ...sampleExistingResult };
};
