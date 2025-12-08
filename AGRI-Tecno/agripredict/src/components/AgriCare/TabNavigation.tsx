import { Sprout, Stethoscope } from "lucide-react";

interface TabNavigationProps {
  activeTab: "new" | "existing";
  onTabChange: (tab: "new" | "existing") => void;
}

const TabNavigation = ({ activeTab, onTabChange }: TabNavigationProps) => {
  return (
    <div
      className="flex bg-muted/50 rounded-t-2xl p-1"
      role="tablist"
      aria-label="Prediction type tabs"
    >
      <button
        role="tab"
        aria-selected={activeTab === "new"}
        aria-controls="newCropPanel"
        id="newCropTab"
        onClick={() => onTabChange("new")}
        className={`flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl font-semibold transition-all duration-300
          ${
            activeTab === "new"
              ? "bg-card text-primary shadow-md"
              : "text-muted-foreground hover:text-foreground hover:bg-card/50"
          }`}
      >
        <Sprout className="w-5 h-5" />
        <span className="hidden sm:inline">New Crop Prediction</span>
        <span className="sm:hidden">New Crop</span>
      </button>
    </div>
  );
};

export default TabNavigation;
