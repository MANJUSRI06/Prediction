import { Leaf } from "lucide-react";

interface LoadingSpinnerProps {
  message?: string;
  size?: "sm" | "md" | "lg";
}

const LoadingSpinner = ({ message = "Processing...", size = "md" }: LoadingSpinnerProps) => {
  const sizeClasses = {
    sm: "w-8 h-8",
    md: "w-16 h-16",
    lg: "w-24 h-24",
  };

  const iconSizes = {
    sm: "w-4 h-4",
    md: "w-8 h-8",
    lg: "w-12 h-12",
  };

  return (
    <div className="flex flex-col items-center justify-center py-12 animate-fade-in">
      <div className={`${sizeClasses[size]} relative`}>
        {/* Outer spinning ring */}
        <div className="absolute inset-0 border-4 border-primary/20 rounded-full" />
        <div className="absolute inset-0 border-4 border-transparent border-t-primary rounded-full animate-spin-slow" />
        
        {/* Center icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <Leaf className={`${iconSizes[size]} text-primary animate-pulse-gentle`} />
        </div>
      </div>
      
      {message && (
        <p className="mt-4 text-muted-foreground font-medium animate-pulse-gentle">
          {message}
        </p>
      )}
    </div>
  );
};

export default LoadingSpinner;
