import { useState, useCallback } from "react";
import Header from "@/components/AgriCare/Header";
import TabNavigation from "@/components/AgriCare/TabNavigation";
import NewCropForm, {
  NewCropFormData,
} from "@/components/AgriCare/NewCropForm";
import NewCropResults, {
  NewCropResultData,
} from "@/components/AgriCare/NewCropResults";
import LoadingSpinner from "@/components/AgriCare/LoadingSpinner";
import ToastContainer, { ToastMessage } from "@/components/AgriCare/Toast";
import { populateNewCropResults } from "@/components/AgriCare/sampleData";

const Index = () => {
  const [activeTab, setActiveTab] = useState<"new" | "existing">("new");
  const [isLoading, setIsLoading] = useState(false);
  const [newCropResults, setNewCropResults] =
    useState<NewCropResultData | null>(null);
  const [farmSize, setFarmSize] = useState(5);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = useCallback(
    (type: ToastMessage["type"], title: string, message?: string) => {
      const id = Date.now().toString();
      setToasts((prev) => [...prev, { id, type, title, message }]);
    },
    []
  );

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const handleNewCropSubmit = async (data: NewCropFormData) => {
    setIsLoading(true);
    setFarmSize(parseFloat(data.farmSize) || 1);

    try {
      // Build FormData for /crop-insights endpoint (no soil image required anymore)
      const form = new FormData();
      form.append("crop", data.crop);
      form.append("soil_image_confidence", "0.85");
      form.append("farm_size_acres", data.farmSize || "1.0");
      if (data.latitude) form.append("latitude", data.latitude);
      if (data.longitude) form.append("longitude", data.longitude);
      if (data.sowingDate) form.append("sowing_date", data.sowingDate);
      form.append("season", "Kharif"); // Default season

      const resp = await fetch("http://127.0.0.1:8000/crop-insights", {
        method: "POST",
        body: form,
      });

      if (!resp.ok) {
        const err = await resp.json().catch(() => ({ error: resp.statusText }));
        throw new Error(err.error || err.detail || "Crop insights failed");
      }

      const body = await resp.json();

      if (!body.success || !body.insights) {
        throw new Error("Invalid response format from backend");
      }

      const insights = body.insights;

      // Attempt to get UI-specific sections from backend via /ui-predictions
      try {
        const uiForm = new FormData();
        uiForm.append("crop", data.crop);
        // prefer predicted yield percent if backend provided it
        const predictedPct =
          insights?.prediction_metadata?.predicted_yield_percent || 70;
        uiForm.append("predicted_yield_percent", String(predictedPct));
        // pass simple weather defaults or extracted values
        const humidity = insights?.weather?.humidity || 70;
        const temperature = insights?.weather?.temperature || 25;
        uiForm.append("humidity", String(humidity));
        uiForm.append("temperature", String(temperature));
        uiForm.append("season", insights?.season || "Kharif");
        if (data.sowingDate) uiForm.append("sowing_date", data.sowingDate);

        const uiResp = await fetch("http://127.0.0.1:8000/ui-predictions", {
          method: "POST",
          body: uiForm,
        });

        if (!uiResp.ok) {
          // fallback: still map from insights if UI endpoint fails
          throw new Error("UI predictions endpoint failed");
        }

        const uiBody = await uiResp.json();
        const preds = uiBody.predictions || uiBody;

        const farmSizeValue = parseFloat(data.farmSize) || 1.0;
        const updated: NewCropResultData = {
          predictedYieldPct: predictedPct,
          predictedYieldQtyPerAcre:
            insights.predicted_yield_quintals_per_acre || 25,
          totalYield: Math.round((predictedPct || 70) * farmSizeValue),
          weatherRecommendation:
            insights.irrigation_schedule?.[0]?.reason ||
            "Optimal conditions for crop growth",
          weatherRisk: "low",
          soilSuggestions: {
            nitrogen: {
              value: Math.round(
                insights.soil_health?.nitrogen?.recommended_mg_per_kg || 100
              ),
              status: "Adjusted",
              suggestion:
                insights.soil_health?.nitrogen?.interpretation ||
                "Apply nitrogen as per crop requirement",
            },
            phosphorus: {
              value: Math.round(
                insights.soil_health?.phosphorus?.recommended_mg_per_kg || 50
              ),
              status: "Moderate",
              suggestion:
                insights.soil_health?.phosphorus?.interpretation ||
                "Apply phosphorus as per crop requirement",
            },
            potassium: {
              value: Math.round(
                insights.soil_health?.potassium?.recommended_mg_per_kg || 40
              ),
              status: "Moderate",
              suggestion:
                insights.soil_health?.potassium?.interpretation ||
                "Apply potassium as per crop requirement",
            },
            ph: {
              value: Number(
                (insights.soil_health?.pH?.recommended_value || 7.0).toFixed(1)
              ),
              status: "Good",
              suggestion:
                insights.soil_health?.pH?.interpretation ||
                "Soil pH is within acceptable range",
            },
          },
          irrigationSchedule:
            insights.irrigation_schedule?.map((day: any) => ({
              day: day.day,
              amount: `${day.irrigation_mm}mm`,
              weather: day.weather_condition,
              skip: day.action === "Skip",
            })) || [],
          irrigationAlert: "Water crops based on daily schedule",
          fertilizerRecommendation: {
            ratio: insights.fertilizer_plan?.npk_ratio || "3:1:1",
            important:
              insights.fertilizer_plan?.critical_timing ||
              "Apply at flowering stage",
            splits:
              insights.fertilizer_plan?.application_schedule?.map(
                (app: any) => ({
                  stage: app.crop_stage || "Growth",
                  day: 0,
                  fertilizer: app.fertilizer_type || "NPK",
                })
              ) || [],
          },
          // Use UI predictor outputs when available (with multiple fallback keys checked)
          growthStages:
            (
              preds.crop_growth_stages ||
              preds.growth_stages ||
              preds.crop_growth ||
              []
            ).map((s: any) => ({
              name: s.name || s.stage_name || "Stage",
              days: String(s.duration_days || s.days || s.length || "30"),
              current: !!s.current,
              icon: s.icon || "🌱",
            })) || [],
          pestRisks:
            (
              preds.pest_risk_assessment ||
              preds.pest_risk ||
              preds.pests ||
              []
            ).map((p: any) => ({
              name: p.name || p.pest || "Pest",
              level:
                (p.risk_level || p.level || p.risk || "low").toLowerCase() ===
                "high"
                  ? "high"
                  : (
                      p.risk_level ||
                      p.level ||
                      p.risk ||
                      "low"
                    ).toLowerCase() === "medium"
                  ? "medium"
                  : "low",
            })) || [],
          costProfit: {
            costPerAcre: Math.round(
              insights.economics?.cost_per_acre ||
                preds.economics?.cost_per_acre ||
                15000
            ),
            revenuePerAcre: Math.round(
              insights.economics?.revenue_per_acre ||
                preds.economics?.revenue_per_acre ||
                30000
            ),
            profitPerAcre: Math.round(
              (insights.economics?.revenue_per_acre ||
                preds.economics?.revenue_per_acre ||
                30000) -
                (insights.economics?.cost_per_acre ||
                  preds.economics?.cost_per_acre ||
                  15000)
            ),
          },
          seasonComparison: {
            changePercent:
              preds.season_comparison?.change_percent ||
              preds.seasonComparison?.changePercent ||
              0,
            trend:
              preds.season_comparison?.trend ||
              preds.seasonComparison?.trend ||
              "flat",
          },
          blockDiagramTasks:
            (
              preds.farming_schedule ||
              preds.farming_tasks ||
              preds.block_diagram ||
              []
            ).map((task: any, idx: number) => ({
              day: task.day || idx + 1,
              title: task.title || task.task || `Day ${idx + 1}`,
              description: task.description || task.note || "",
              type: (task.type || "sowing") as const,
            })) || [],
        };

        setNewCropResults(updated);
        addToast(
          "success",
          "Prediction Complete",
          `Dynamic insights generated for ${data.crop}!`
        );
      } catch (uiErr) {
        // If UI predictor call fails, fallback to previous mapping approach using insights only
        console.warn(
          "UI predictions fetch failed, falling back to insights mapping: ",
          uiErr
        );
        const farmSizeValue = parseFloat(data.farmSize) || 1.0;
        const updated: NewCropResultData = {
          predictedYieldPct:
            insights.prediction_metadata?.predicted_yield_percent || 70,
          predictedYieldQtyPerAcre: 25,
          totalYield: Math.round(
            (insights.prediction_metadata?.predicted_yield_percent || 70) *
              farmSizeValue
          ),
          weatherRecommendation:
            insights.irrigation_schedule?.[0]?.reason ||
            "Optimal conditions for crop growth",
          weatherRisk: "low",
          soilSuggestions: {
            nitrogen: {
              value: Math.round(
                insights.soil_health?.nitrogen?.recommended_mg_per_kg || 100
              ),
              status: "Adjusted",
              suggestion:
                insights.soil_health?.nitrogen?.interpretation ||
                "Apply nitrogen as per crop requirement",
            },
            phosphorus: {
              value: Math.round(
                insights.soil_health?.phosphorus?.recommended_mg_per_kg || 50
              ),
              status: "Moderate",
              suggestion:
                insights.soil_health?.phosphorus?.interpretation ||
                "Apply phosphorus as per crop requirement",
            },
            potassium: {
              value: Math.round(
                insights.soil_health?.potassium?.recommended_mg_per_kg || 40
              ),
              status: "Moderate",
              suggestion:
                insights.soil_health?.potassium?.interpretation ||
                "Apply potassium as per crop requirement",
            },
            ph: {
              value: Number(
                (insights.soil_health?.pH?.recommended_value || 7.0).toFixed(1)
              ),
              status: "Good",
              suggestion:
                insights.soil_health?.pH?.interpretation ||
                "Soil pH is within acceptable range",
            },
          },
          irrigationSchedule:
            insights.irrigation_schedule?.map((day: any) => ({
              day: day.day,
              amount: `${day.irrigation_mm}mm`,
              weather: day.weather_condition,
              skip: day.action === "Skip",
            })) || [],
          irrigationAlert: "Water crops based on daily schedule",
          fertilizerRecommendation: {
            ratio: insights.fertilizer_plan?.npk_ratio || "3:1:1",
            important:
              insights.fertilizer_plan?.critical_timing ||
              "Apply at flowering stage",
            splits:
              insights.fertilizer_plan?.application_schedule?.map(
                (app: any) => ({
                  stage: app.crop_stage || "Growth",
                  day: 0,
                  fertilizer: app.fertilizer_type || "NPK",
                })
              ) || [],
          },
          growthStages:
            insights.growth_stages?.stages?.map((stage: any) => ({
              name: stage.name || "Stage",
              days: String(stage.duration_days) || "30",
              current: false,
              icon: "🌱",
            })) || [],
          pestRisks:
            insights.pest_risk?.map((pest: any) => ({
              name: pest.name || "Pest",
              level:
                pest.risk_level === "High"
                  ? "high"
                  : pest.risk_level === "Medium"
                  ? "medium"
                  : "low",
            })) || [],
          costProfit: {
            costPerAcre: Math.round(insights.economics?.cost_per_acre || 15000),
            revenuePerAcre: Math.round(
              insights.economics?.revenue_per_acre || 30000
            ),
            profitPerAcre: Math.round(
              (insights.economics?.revenue_per_acre || 30000) -
                (insights.economics?.cost_per_acre || 15000)
            ),
          },
          seasonComparison: {
            changePercent: 5,
            trend: "up",
          },
          blockDiagramTasks:
            insights.farming_tasks?.map((task: any, idx: number) => ({
              day: idx + 1,
              title: task.task || "Task",
              description: task.description || "",
              type: "sowing" as const,
            })) || [],
        };

        setNewCropResults(updated);
        addToast(
          "warning",
          "Fallback Used",
          "UI predictor unavailable — showing insight-based results."
        );
      }
    } catch (error: any) {
      console.error("New crop prediction error:", error);
      addToast(
        "destructive",
        "Prediction Error",
        error?.message || "Failed to get prediction from backend."
      );
    } finally {
      setIsLoading(false);
    }
  };

  

  const handleNewCropReset = () => {
    setNewCropResults(null);
  };

  

  const handleEnableAlerts = () => {
    addToast(
      "info",
      "Alerts Enabled",
      "You'll receive fertilizer and irrigation reminders."
    );
  };
  

  return (
    <div className="min-h-screen bg-gradient-agri">
      <Header />

      <main className="container mx-auto px-4 py-6 max-w-7xl">
        {/* Tab Navigation */}
        <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

        {/* Tab Panels */}
        <div className="bg-card rounded-b-2xl rounded-tr-2xl shadow-agri-lg overflow-hidden">
          {/* New Crop Tab */}
          <div
            id="newCropPanel"
            role="tabpanel"
            aria-labelledby="newCropTab"
            hidden={activeTab !== "new"}
            className={`transition-all duration-300 ${
              activeTab === "new" ? "animate-fade-in" : ""
            }`}
          >
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 p-6">
              {/* Form Column */}
              <div className="agri-card-elevated">
                <h2 className="text-xl font-bold text-primary mb-6">
                  New Crop Prediction
                </h2>
                <p className="text-muted-foreground mb-6">
                  Plan your crop before sowing. Get yield predictions,
                  schedules, and recommendations.
                </p>
                <NewCropForm
                  onSubmit={handleNewCropSubmit}
                  onReset={handleNewCropReset}
                  isLoading={isLoading}
                />
              </div>

              {/* Results Column */}
              <div className="agri-card-elevated">
                <h2 className="text-xl font-bold text-primary mb-6">
                  Prediction Results
                </h2>
                {isLoading && activeTab === "new" ? (
                  <LoadingSpinner message="Analyzing crop data..." />
                ) : newCropResults ? (
                  <NewCropResults
                    data={newCropResults}
                    farmSize={farmSize}
                    onEnableAlerts={handleEnableAlerts}
                  />
                ) : (
                  <div className="flex flex-col items-center justify-center py-16 text-center">
                    <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center mb-4">
                      <span className="text-4xl">🌱</span>
                    </div>
                    <p className="text-muted-foreground">
                      Fill out the form and click "Predict & Recommend" to see
                      your results here.
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Existing Crop Tab removed — app now focuses on New Crop Prediction only */}
        </div>

        {/* Footer note for developers */}
        <footer className="mt-8 text-center text-sm text-muted-foreground">
          <p>
            AgriCare — Empowering Odisha Farmers with AI-powered Crop
            Intelligence
          </p>
          {/* 
            Developer Notes:
            - Connect to /api/predict/new for Tab A predictions
            - Connect to /api/predict/existing for Tab B diagnosis
            - Image processing API should return: { issue: string, confidence: number, boxes: [...] }
            - See sampleData.ts for expected request/response schemas
          */}
        </footer>
      </main>

      {/* Toast Notifications */}
      <ToastContainer toasts={toasts} onClose={removeToast} />
    </div>
  );
};

export default Index;
