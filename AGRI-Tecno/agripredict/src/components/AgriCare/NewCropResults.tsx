import {
  Download,
  Share2,
  Bell,
  AlertTriangle,
  CheckCircle,
  Droplets,
  Leaf,
  Bug,
  TrendingUp,
  DollarSign,
} from "lucide-react";
import { useCallback, useState } from "react";
import ProgressRing from "./ProgressRing";
import BlockDiagram from "./BlockDiagram";
import {
  generateNewCropReportPDF,
  generateNewCropReportDOCX,
} from "@/lib/reportGenerator";
import { useToast } from "@/hooks/use-toast";

export interface NewCropResultData {
  predictedYieldPct: number;
  predictedYieldQtyPerAcre: number;
  totalYield: number;
  weatherRecommendation: string;
  weatherRisk: "low" | "medium" | "high";
  soilSuggestions: {
    nitrogen: { value: number; status: string; suggestion: string };
    phosphorus: { value: number; status: string; suggestion: string };
    potassium: { value: number; status: string; suggestion: string };
    ph: { value: number; status: string; suggestion: string };
  };
  irrigationSchedule: {
    day: string;
    amount: string;
    weather: string;
    skip?: boolean;
  }[];
  irrigationAlert: string;
  fertilizerRecommendation: {
    ratio: string;
    important: string;
    splits: { stage: string; day: number; fertilizer: string }[];
  };
  growthStages: {
    name: string;
    days: string;
    current: boolean;
    icon: string;
  }[];
  pestRisks: { name: string; level: "low" | "medium" | "high" }[];
  costProfit: {
    costPerAcre: number;
    revenuePerAcre: number;
    profitPerAcre: number;
  };
  seasonComparison: {
    changePercent: number;
    trend: "up" | "down" | "stable";
  };
  blockDiagramTasks: {
    day: number;
    title: string;
    description: string;
    type:
      | "sowing"
      | "irrigation"
      | "fertilizer"
      | "growth"
      | "harvest"
      | "pest";
  }[];
}

interface NewCropResultsProps {
  data: NewCropResultData | null;
  farmSize: number;
  onEnableAlerts: () => void;
}

const NewCropResults = ({
  data,
  farmSize,
  onEnableAlerts,
}: NewCropResultsProps) => {
  if (!data) return null;

  const [isDownloading, setIsDownloading] = useState(false);
  const { toast } = useToast();

  const handleDownloadPDF = useCallback(async () => {
    setIsDownloading(true);
    try {
      const fileName = `crop_yield_prediction_${
        new Date().toISOString().split("T")[0]
      }.pdf`;
      await generateNewCropReportPDF(data, farmSize, fileName);
      toast({
        title: "Success",
        description: "Prediction report downloaded as PDF",
      });
    } catch (error) {
      console.error("Error downloading PDF:", error);
      toast({
        title: "Error",
        description: "Failed to download PDF report",
        variant: "destructive",
      });
    } finally {
      setIsDownloading(false);
    }
  }, [data, farmSize, toast]);

  const handleDownloadDOCX = useCallback(async () => {
    setIsDownloading(true);
    try {
      const fileName = `crop_yield_prediction_${
        new Date().toISOString().split("T")[0]
      }.docx`;
      await generateNewCropReportDOCX(data, farmSize, fileName);
      toast({
        title: "Success",
        description: "Prediction report downloaded as DOCX",
      });
    } catch (error) {
      console.error("Error downloading DOCX:", error);
      toast({
        title: "Error",
        description: "Failed to download DOCX report",
        variant: "destructive",
      });
    } finally {
      setIsDownloading(false);
    }
  }, [data, farmSize, toast]);

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "low":
        return <span className="agri-badge-success">Low Risk</span>;
      case "medium":
        return <span className="agri-badge-warning">Medium Risk</span>;
      case "high":
        return <span className="agri-badge-danger">High Risk</span>;
      default:
        return <span className="agri-badge-info">{risk}</span>;
    }
  };

  const getStatusBadge = (status: string) => {
    if (
      status.toLowerCase().includes("optimal") ||
      status.toLowerCase().includes("good")
    ) {
      return <span className="agri-badge-success">{status}</span>;
    }
    if (status.toLowerCase().includes("low")) {
      return <span className="agri-badge-danger">{status}</span>;
    }
    return <span className="agri-badge-warning">{status}</span>;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Yield Prediction */}
      <div className="agri-card animate-slide-up">
        <h3 className="text-lg font-semibold text-primary mb-4 flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Predicted Yield
        </h3>
        <div className="flex items-center gap-6">
          <div id="predictedYieldPct">
            <ProgressRing
              percentage={data.predictedYieldPct}
              label="Success Rate"
            />
          </div>
          <div className="flex-1">
            <p className="text-sm text-muted-foreground">Per Acre</p>
            <p
              id="predictedYieldQty"
              className="text-2xl font-bold text-foreground"
            >
              {data.predictedYieldQtyPerAcre} quintals
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Total for {farmSize} acres
            </p>
            <p className="text-xl font-semibold text-primary">
              {data.totalYield} quintals
            </p>
          </div>
        </div>
      </div>

      {/* Weather Recommendation */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.1s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-3 flex items-center gap-2">
          <AlertTriangle className="w-5 h-5" />
          Weather Recommendation
        </h3>
        <p id="weatherRecommendation" className="text-foreground mb-3">
          {data.weatherRecommendation}
        </p>
        <div id="weatherRiskBadge">{getRiskBadge(data.weatherRisk)}</div>
      </div>

      {/* Soil Suggestions */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.15s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-4 flex items-center gap-2">
          <Leaf className="w-5 h-5" />
          Soil Health Suggestions
        </h3>
        <div id="soilSuggestions" className="space-y-4">
          {Object.entries(data.soilSuggestions).map(([key, item]) => (
            <div
              key={key}
              className="flex items-start justify-between pb-3 border-b border-border last:border-0"
            >
              <div>
                <p className="font-medium capitalize">
                  {key === "ph" ? "pH" : key} ({key === "ph" ? "" : "N/P/K"}):{" "}
                  {item.value} {key !== "ph" ? "mg/kg" : ""}
                </p>
                <p className="text-sm text-muted-foreground">
                  {item.suggestion}
                </p>
              </div>
              {getStatusBadge(item.status)}
            </div>
          ))}
        </div>
      </div>

      {/* Irrigation Schedule */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.2s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-4 flex items-center gap-2">
          <Droplets className="w-5 h-5" />
          Irrigation Schedule
        </h3>
        <div className="bg-secondary/20 text-secondary-foreground px-4 py-2 rounded-lg mb-4">
          <span className="font-medium">Current Week's Focus: </span>
          <span id="irrigationAlert">{data.irrigationAlert}</span>
        </div>
        <div id="irrigationSchedule" className="space-y-3">
          {data.irrigationSchedule.map((item, index) => (
            <div key={index} className="flex items-center gap-3">
              {item.skip ? (
                <span className="w-6 h-6 rounded-full bg-destructive/20 flex items-center justify-center">
                  <span className="text-destructive text-xs">✕</span>
                </span>
              ) : (
                <CheckCircle className="w-5 h-5 text-success" />
              )}
              <div className="flex-1">
                <span
                  className={`font-medium ${
                    item.skip ? "text-muted-foreground" : "text-primary"
                  }`}
                >
                  {item.day}: {item.amount}
                </span>
                <span className="text-sm text-muted-foreground ml-2">
                  {item.weather}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Fertilizer Recommendation */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.25s" }}
      >
        <div className="flex items-start justify-between mb-4">
          <h3 className="text-lg font-semibold text-primary flex items-center gap-2">
            <Leaf className="w-5 h-5" />
            Fertilizer Recommendation
          </h3>
          <button
            id="fertilizerNotifyBtn"
            onClick={onEnableAlerts}
            className="agri-btn-ghost flex items-center gap-1 text-sm"
            aria-label="Enable fertilizer alerts"
          >
            <Bell className="w-4 h-4" />
            Enable Alerts
          </button>
        </div>
        <div id="fertilizerRecommendation">
          <p className="text-2xl font-bold text-foreground mb-2">
            NPK Ratio: {data.fertilizerRecommendation.ratio}
          </p>
          <div className="bg-secondary/20 border border-secondary/30 rounded-lg p-3 mb-4">
            <p className="text-sm font-medium text-secondary-foreground">
              ⚠️ Important: {data.fertilizerRecommendation.important}
            </p>
          </div>
          <h4 className="font-medium mb-2">Application Splits:</h4>
          <div className="space-y-2">
            {data.fertilizerRecommendation.splits.map((split, index) => (
              <div key={index} className="text-sm">
                <span className="font-medium">
                  {split.stage} (Day {split.day})
                </span>
                <span className="text-muted-foreground ml-2">
                  {split.fertilizer}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Growth Stage Prediction */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.3s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-4">
          Crop Growth Stage Prediction
        </h3>
        <div id="growthStagePrediction" className="space-y-3">
          {data.growthStages.map((stage, index) => (
            <div
              key={index}
              className={`flex items-center gap-3 ${
                stage.current
                  ? "text-primary font-medium"
                  : "text-muted-foreground"
              }`}
            >
              <span
                className={`w-3 h-3 rounded-full ${
                  stage.current ? "bg-primary" : "bg-border"
                }`}
              />
              <span>{stage.name}</span>
              <span className="text-sm">({stage.days})</span>
              {stage.current && (
                <span className="agri-badge-success ml-auto">Current</span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Pest Risk */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.35s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-4 flex items-center gap-2">
          <Bug className="w-5 h-5" />
          Pest Risk Assessment
        </h3>
        <div id="pestRiskList" className="space-y-2">
          {data.pestRisks.map((pest, index) => (
            <div
              key={index}
              className="flex items-center justify-between py-2 border-b border-border last:border-0"
            >
              <span className="font-medium">{pest.name}</span>
              {getRiskBadge(pest.level)}
            </div>
          ))}
        </div>
      </div>

      {/* Cost & Profit */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.4s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-4 flex items-center gap-2">
          <DollarSign className="w-5 h-5" />
          Cost & Profit Estimate (per acre)
        </h3>
        <div
          id="costProfitEstimate"
          className="grid grid-cols-3 gap-4 text-center"
        >
          <div className="p-3 bg-destructive/10 rounded-xl">
            <p className="text-sm text-muted-foreground">Cost</p>
            <p className="text-lg font-bold text-destructive">
              ₹{data.costProfit.costPerAcre.toLocaleString()}
            </p>
          </div>
          <div className="p-3 bg-primary/10 rounded-xl">
            <p className="text-sm text-muted-foreground">Revenue</p>
            <p className="text-lg font-bold text-primary">
              ₹{data.costProfit.revenuePerAcre.toLocaleString()}
            </p>
          </div>
          <div className="p-3 bg-success/10 rounded-xl">
            <p className="text-sm text-muted-foreground">Profit</p>
            <p className="text-lg font-bold text-success">
              ₹{data.costProfit.profitPerAcre.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      {/* Season Comparison */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.45s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-3">
          Season Comparison
        </h3>
        <div id="seasonComparison" className="flex items-center gap-4">
          <div
            className={`text-2xl font-bold ${
              data.seasonComparison.trend === "up"
                ? "text-success"
                : data.seasonComparison.trend === "down"
                ? "text-destructive"
                : "text-muted-foreground"
            }`}
          >
            {data.seasonComparison.trend === "up"
              ? "↑"
              : data.seasonComparison.trend === "down"
              ? "↓"
              : "→"}
            {Math.abs(data.seasonComparison.changePercent)}%
          </div>
          <p className="text-muted-foreground">compared to previous seasons</p>
        </div>
      </div>

      {/* Block Diagram */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.5s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-4">
          Farming Schedule (Day-wise Tasks)
        </h3>
        <BlockDiagram tasks={data.blockDiagramTasks} currentDay={10} />
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col gap-3 pt-4">
        <button
          onClick={handleDownloadPDF}
          disabled={isDownloading}
          className="agri-btn-primary flex-1 flex items-center justify-center gap-2"
          aria-label="Download report as PDF"
        >
          <Download className="w-5 h-5" />
          {isDownloading ? "Generating..." : "Download as PDF"}
        </button>
        <button
          onClick={handleDownloadDOCX}
          disabled={isDownloading}
          className="agri-btn-primary flex-1 flex items-center justify-center gap-2"
          aria-label="Download report as DOCX"
        >
          <Download className="w-5 h-5" />
          {isDownloading ? "Generating..." : "Download as Word"}
        </button>
        <button
          id="shareBtn"
          className="agri-btn-outline flex items-center justify-center gap-2"
          aria-label="Share prediction results"
        >
          <Share2 className="w-5 h-5" />
          Share
        </button>
      </div>
    </div>
  );
};

export default NewCropResults;
