import { Sprout, Droplets, Leaf, Sun, Scissors, Package } from "lucide-react";

interface Task {
  day: number;
  title: string;
  description: string;
  type: "sowing" | "irrigation" | "fertilizer" | "growth" | "harvest" | "pest";
}

interface BlockDiagramProps {
  tasks: Task[];
  currentDay?: number;
}

const BlockDiagram = ({ tasks, currentDay = 0 }: BlockDiagramProps) => {
  const getIcon = (type: Task["type"]) => {
    switch (type) {
      case "sowing":
        return <Sprout className="w-5 h-5" />;
      case "irrigation":
        return <Droplets className="w-5 h-5" />;
      case "fertilizer":
        return <Leaf className="w-5 h-5" />;
      case "growth":
        return <Sun className="w-5 h-5" />;
      case "harvest":
        return <Scissors className="w-5 h-5" />;
      case "pest":
        return <Package className="w-5 h-5" />;
      default:
        return <Leaf className="w-5 h-5" />;
    }
  };

  const getTypeColor = (type: Task["type"], isPast: boolean) => {
    if (isPast) return "bg-primary text-primary-foreground";
    
    switch (type) {
      case "sowing":
        return "bg-primary/20 text-primary border-2 border-primary";
      case "irrigation":
        return "bg-blue-100 text-blue-700 border-2 border-blue-300";
      case "fertilizer":
        return "bg-secondary/30 text-secondary-foreground border-2 border-secondary";
      case "growth":
        return "bg-success/20 text-success border-2 border-success";
      case "harvest":
        return "bg-amber-100 text-amber-700 border-2 border-amber-300";
      case "pest":
        return "bg-red-100 text-red-700 border-2 border-red-300";
      default:
        return "bg-muted text-muted-foreground border-2 border-border";
    }
  };

  return (
    <div id="blockDiagram" className="relative overflow-x-auto pb-4">
      <div className="flex items-start gap-2 min-w-max">
        {tasks.map((task, index) => {
          const isPast = task.day <= currentDay;
          const isCurrent = task.day === currentDay;
          
          return (
            <div key={index} className="flex items-start">
              {/* Task block */}
              <div
                className={`relative flex flex-col items-center p-3 rounded-xl min-w-[100px] transition-all duration-300
                  ${getTypeColor(task.type, isPast)}
                  ${isCurrent ? "ring-4 ring-secondary shadow-agri-glow scale-105" : ""}
                `}
              >
                <div className="flex items-center justify-center w-10 h-10 rounded-full bg-card/50 mb-2">
                  {getIcon(task.type)}
                </div>
                <span className="text-xs font-bold">Day {task.day}</span>
                <span className="text-[10px] font-medium text-center mt-1 leading-tight">
                  {task.title}
                </span>
              </div>
              
              {/* Connector line */}
              {index < tasks.length - 1 && (
                <div className="flex items-center h-20 px-1">
                  <div className={`w-4 h-1 ${task.day <= currentDay ? "bg-primary" : "bg-border"} rounded-full`} />
                  <div className={`w-2 h-2 ${task.day <= currentDay ? "bg-primary" : "bg-border"} rounded-full`} />
                </div>
              )}
            </div>
          );
        })}
      </div>
      
      {/* Legend */}
      <div className="flex flex-wrap gap-4 mt-6 pt-4 border-t border-border">
        <div className="flex items-center gap-2 text-xs">
          <div className="w-3 h-3 rounded-full bg-primary" />
          <span className="text-muted-foreground">Completed</span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <div className="w-3 h-3 rounded-full bg-secondary ring-2 ring-secondary" />
          <span className="text-muted-foreground">Current</span>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <div className="w-3 h-3 rounded-full bg-muted border-2 border-border" />
          <span className="text-muted-foreground">Upcoming</span>
        </div>
      </div>
    </div>
  );
};

export default BlockDiagram;
