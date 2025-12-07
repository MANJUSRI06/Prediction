import { useState, useRef } from "react";
import { Upload, Camera, X, ChevronLeft, ChevronRight, Image } from "lucide-react";

interface ImageUploaderProps {
  id: string;
  accept?: string;
  multiple?: boolean;
  label?: string;
  placeholder?: string;
  onImagesChange?: (images: File[]) => void;
}

const ImageUploader = ({
  id,
  accept = "image/*",
  multiple = true,
  label = "Upload Images",
  placeholder = "Drop images here or click to upload",
  onImagesChange,
}: ImageUploaderProps) => {
  const [images, setImages] = useState<{ file: File; preview: string }[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (files: FileList | null) => {
    if (!files) return;
    const fileArray = Array.from(files);
    const maxSize = 10 * 1024 * 1024; // 10MB
    const accepted: { file: File; preview: string }[] = [];
    const skipped: string[] = [];

    fileArray.forEach((file) => {
      if (!file.type.startsWith('image/')) {
        skipped.push(file.name + ' (not an image)');
        return;
      }
      if (file.size > maxSize) {
        skipped.push(file.name + ' (too large)');
        return;
      }
      accepted.push({ file, preview: URL.createObjectURL(file) });
    });

    if (accepted.length === 0 && skipped.length > 0) {
      // Inform the user that their files were skipped
      window.alert('Some files were skipped: ' + skipped.join(', '));
      return;
    }

    const updatedImages = multiple ? [...images, ...accepted] : accepted;
    setImages(updatedImages);
    onImagesChange?.(updatedImages.map((img) => img.file));
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFiles(e.dataTransfer.files);
  };

  const removeImage = (index: number) => {
    const newImages = images.filter((_, i) => i !== index);
    setImages(newImages);
    onImagesChange?.(newImages.map((img) => img.file));
    if (currentIndex >= newImages.length && currentIndex > 0) {
      setCurrentIndex(newImages.length - 1);
    }
  };

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length);
  };

  return (
    <div className="space-y-3">
      {/* Upload area */}
      <div
        className={`relative border-2 border-dashed rounded-2xl p-8 transition-all duration-300 cursor-pointer
          bg-primary/5 shadow-agri
          ${isDragging 
            ? "border-primary bg-primary/10 shadow-agri-lg scale-[1.02]" 
            : "border-primary/40 hover:border-primary hover:bg-primary/8 hover:shadow-agri-lg"
          }`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          id={id}
          type="file"
          accept={accept}
          multiple={multiple}
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
          aria-label={label}
        />
        
        <div className="flex flex-col items-center gap-4">
          {/* Camera Icon */}
          <div className="w-16 h-16 bg-primary/15 rounded-2xl flex items-center justify-center">
            <Camera className="w-8 h-8 text-primary" />
          </div>
          
          {/* Primary Text */}
          <p className="text-lg font-semibold text-primary">{label}</p>
          
          {/* Secondary Text */}
          <p className="text-sm text-muted-foreground text-center max-w-[220px]">
            {placeholder}
          </p>
        </div>
      </div>

      {/* Image carousel */}
      {images.length > 0 && (
        <div className="relative rounded-xl overflow-hidden bg-muted/30 border border-border">
          {/* Main image */}
          <div className="relative aspect-video">
            <img
              src={images[currentIndex]?.preview}
              alt={`Upload ${currentIndex + 1}`}
              className="w-full h-full object-contain"
            />
            
            {/* Remove button */}
            <button
              onClick={(e) => { e.stopPropagation(); removeImage(currentIndex); }}
              className="absolute top-2 right-2 w-8 h-8 bg-destructive/90 text-destructive-foreground rounded-full 
                flex items-center justify-center hover:bg-destructive transition-colors"
              aria-label="Remove image"
            >
              <X className="w-4 h-4" />
            </button>

            {/* Navigation arrows */}
            {images.length > 1 && (
              <>
                <button
                  onClick={(e) => { e.stopPropagation(); prevImage(); }}
                  className="absolute left-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-card/90 rounded-full 
                    flex items-center justify-center hover:bg-card transition-colors shadow-md"
                  aria-label="Previous image"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={(e) => { e.stopPropagation(); nextImage(); }}
                  className="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-card/90 rounded-full 
                    flex items-center justify-center hover:bg-card transition-colors shadow-md"
                  aria-label="Next image"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </>
            )}
          </div>

          {/* Thumbnails */}
          {images.length > 1 && (
            <div className="flex gap-2 p-3 overflow-x-auto">
              {images.map((img, index) => (
                <button
                  key={index}
                  onClick={(e) => { e.stopPropagation(); setCurrentIndex(index); }}
                  className={`flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 transition-all
                    ${index === currentIndex 
                      ? "border-primary ring-2 ring-primary/30" 
                      : "border-transparent hover:border-border"
                    }`}
                >
                  <img src={img.preview} alt="" className="w-full h-full object-cover" />
                </button>
              ))}
            </div>
          )}

          {/* Counter */}
          <div className="absolute bottom-3 left-3 px-2 py-1 bg-card/90 rounded-full text-xs font-medium">
            <Image className="w-3 h-3 inline mr-1" />
            {currentIndex + 1} / {images.length}
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;
