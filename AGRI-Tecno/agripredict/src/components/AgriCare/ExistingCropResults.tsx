import {
  Download,
  Share2,
  Eye,
  AlertCircle,
  CheckCircle,
  Droplets,
  Leaf,
  DollarSign,
  TrendingUp,
} from "lucide-react";
import { useCallback, useState } from "react";
import {
  generateExistingCropReportPDF,
  generateExistingCropReportDOCX,
} from "@/lib/reportGenerator";
import { useToast } from "@/hooks/use-toast";

export interface ExistingCropResultData {
  diagnosedIssue: string;
  issueConfidence: number;
  issueEvidence: {
    imageUrl: string;
    boundingBoxes: { x: number; y: number; width: number; height: number }[];
  } | null;
  imageProcessingLog: string;
  soilTypeFromImage: string;
  recommendedCropForSoil: string[];
  remedialActions: string[];
  irrigationAdjustments: string[];
  growthStageExisting: {
    currentStage: string;
    daysToNextStage: number;
    nextStage: string;
  };
  costAdjustmentEstimate: {
    unresolvedLoss: number;
    resolvedGain: number;
  };
  historyComparison: string;
}

interface ExistingCropResultsProps {
  data: ExistingCropResultData | null;
  onShowExplanation: () => void;
}

const ExistingCropResults = ({
  data,
  onShowExplanation,
}: ExistingCropResultsProps) => {
  if (!data) return null;

  const [isDownloading, setIsDownloading] = useState(false);
  const { toast } = useToast();

  const handleDownloadPDF = useCallback(async () => {
    setIsDownloading(true);
    try {
      const fileName = `crop_diagnosis_report_${
        new Date().toISOString().split("T")[0]
      }.pdf`;
      await generateExistingCropReportPDF(data, fileName);
      toast({
        title: "Success",
        description: "Diagnosis report downloaded as PDF",
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
  }, [data, toast]);

  const handleDownloadDOCX = useCallback(async () => {
    setIsDownloading(true);
    try {
      const fileName = `crop_diagnosis_report_${
        new Date().toISOString().split("T")[0]
      }.docx`;
      await generateExistingCropReportDOCX(data, fileName);
      toast({
        title: "Success",
        description: "Diagnosis report downloaded as DOCX",
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
  }, [data, toast]);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 80) return "text-success";
    if (confidence >= 60) return "text-warning";
    return "text-destructive";
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Diagnosed Issue */}
      <div className="agri-card animate-slide-up border-l-4 border-l-destructive">
        <h3 className="text-lg font-semibold text-destructive mb-3 flex items-center gap-2">
          <AlertCircle className="w-5 h-5" />
          Diagnosed Issue
        </h3>
        <div className="flex items-center justify-between mb-3">
          <p id="diagnosedIssue" className="text-xl font-bold text-foreground">
            {data.diagnosedIssue}
          </p>
          <span
            id="issueConfidence"
            className={`text-lg font-bold ${getConfidenceColor(
              data.issueConfidence
            )}`}
          >
            {data.issueConfidence}% confidence
          </span>
        </div>

        {/* Issue Evidence */}
        {data.issueEvidence && (
          <div id="issueEvidence" className="mt-4">
            <p className="text-sm text-muted-foreground mb-2">
              Detected Areas:
            </p>
            <div className="relative rounded-xl overflow-hidden bg-muted/30">
              <img
                src={data.issueEvidence.imageUrl}
                alt="Analyzed plant image"
                className="w-full h-48 object-cover"
              />
              {/* TODO: Render bounding boxes from image-processing API */}
              <div className="absolute inset-0 pointer-events-none">
                {data.issueEvidence.boundingBoxes.map((box, index) => (
                  <div
                    key={index}
                    className="absolute border-2 border-destructive bg-destructive/20 rounded"
                    style={{
                      left: `${box.x}%`,
                      top: `${box.y}%`,
                      width: `${box.width}%`,
                      height: `${box.height}%`,
                    }}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Image Processing Log */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.1s" }}
      >
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-primary flex items-center gap-2">
            <Eye className="w-5 h-5" />
            Detection Analysis
          </h3>
          <button
            onClick={onShowExplanation}
            className="agri-btn-ghost text-sm flex items-center gap-1"
            aria-label="Show model explanation"
          >
            <Eye className="w-4 h-4" />
            Show Heatmap
          </button>
        </div>
        <p id="imageProcessingLog" className="text-muted-foreground">
          {data.imageProcessingLog}
        </p>
        {/* TODO: Add heatmap/feature map overlay when explanation is toggled */}
      </div>

      {/* Soil Type & Recommended Crops */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.15s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-3 flex items-center gap-2">
          <Leaf className="w-5 h-5" />
          Soil Analysis
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Inferred Soil Type</p>
            <p
              id="soilTypeFromImage"
              className="text-lg font-semibold text-foreground"
            >
              {data.soilTypeFromImage}
            </p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">
              Recommended Crops for this Soil
            </p>
            <div
              id="recommendedCropForSoil"
              className="flex flex-wrap gap-2 mt-1"
            >
              {data.recommendedCropForSoil.map((crop, index) => (
                <span key={index} className="agri-badge-info">
                  {crop}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Remedial Actions */}
      <div
        className="agri-card animate-slide-up border-l-4 border-l-success"
        style={{ animationDelay: "0.2s" }}
      >
        <h3 className="text-lg font-semibold text-success mb-4 flex items-center gap-2">
          <CheckCircle className="w-5 h-5" />
          Remedial Actions
        </h3>
        <ul id="remedialActions" className="space-y-3">
          {data.remedialActions.map((action, index) => (
            <li key={index} className="flex items-start gap-3">
              <span className="w-6 h-6 rounded-full bg-success/20 text-success flex items-center justify-center text-sm font-bold flex-shrink-0">
                {index + 1}
              </span>
              <span className="text-foreground">{action}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Irrigation Adjustments */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.25s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-4 flex items-center gap-2">
          <Droplets className="w-5 h-5" />
          Irrigation Adjustments
        </h3>
        <ul id="irrigationAdjustments" className="space-y-2">
          {data.irrigationAdjustments.map((adjustment, index) => (
            <li key={index} className="flex items-center gap-2 text-foreground">
              <Droplets className="w-4 h-4 text-primary flex-shrink-0" />
              {adjustment}
            </li>
          ))}
        </ul>
      </div>

      {/* Growth Stage */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.3s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-3 flex items-center gap-2">
          <TrendingUp className="w-5 h-5" />
          Growth Stage
        </h3>
        <div
          id="growthStageExisting"
          className="grid grid-cols-3 gap-4 text-center"
        >
          <div className="p-3 bg-primary/10 rounded-xl">
            <p className="text-sm text-muted-foreground">Current Stage</p>
            <p className="text-lg font-bold text-primary">
              {data.growthStageExisting.currentStage}
            </p>
          </div>
          <div className="p-3 bg-secondary/20 rounded-xl">
            <p className="text-sm text-muted-foreground">Days to Next</p>
            <p className="text-lg font-bold text-secondary-foreground">
              {data.growthStageExisting.daysToNextStage}
            </p>
          </div>
          <div className="p-3 bg-muted rounded-xl">
            <p className="text-sm text-muted-foreground">Next Stage</p>
            <p className="text-lg font-bold text-foreground">
              {data.growthStageExisting.nextStage}
            </p>
          </div>
        </div>
      </div>

      {/* Cost Adjustment Estimate */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.35s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-4 flex items-center gap-2">
          <DollarSign className="w-5 h-5" />
          Cost Impact Estimate
        </h3>
        <div id="costAdjustmentEstimate" className="grid grid-cols-2 gap-4">
          <div className="p-4 bg-destructive/10 rounded-xl text-center">
            <p className="text-sm text-muted-foreground">If Unresolved</p>
            <p className="text-xl font-bold text-destructive">
              -₹{data.costAdjustmentEstimate.unresolvedLoss.toLocaleString()}
            </p>
            <p className="text-xs text-muted-foreground">potential loss</p>
          </div>
          <div className="p-4 bg-success/10 rounded-xl text-center">
            <p className="text-sm text-muted-foreground">If Resolved</p>
            <p className="text-xl font-bold text-success">
              +₹{data.costAdjustmentEstimate.resolvedGain.toLocaleString()}
            </p>
            <p className="text-xs text-muted-foreground">potential gain</p>
          </div>
        </div>
      </div>

      {/* History Comparison */}
      <div
        className="agri-card animate-slide-up"
        style={{ animationDelay: "0.4s" }}
      >
        <h3 className="text-lg font-semibold text-primary mb-3">
          Season/Field Comparison
        </h3>
        <p id="historyComparisonExisting" className="text-muted-foreground">
          {data.historyComparison}
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col gap-3 pt-4">
        <button
          onClick={handleDownloadPDF}
          disabled={isDownloading}
          className="agri-btn-primary flex-1 flex items-center justify-center gap-2"
          aria-label="Download diagnosis report as PDF"
        >
          <Download className="w-5 h-5" />
          {isDownloading ? "Generating..." : "Download as PDF"}
        </button>
        <button
          onClick={handleDownloadDOCX}
          disabled={isDownloading}
          className="agri-btn-primary flex-1 flex items-center justify-center gap-2"
          aria-label="Download diagnosis report as DOCX"
        >
          <Download className="w-5 h-5" />
          {isDownloading ? "Generating..." : "Download as Word"}
        </button>
        <button
          className="agri-btn-outline flex items-center justify-center gap-2"
          aria-label="Share diagnosis results"
        >
          <Share2 className="w-5 h-5" />
          Share
        </button>
      </div>
    </div>
  );
};

export default ExistingCropResults;
