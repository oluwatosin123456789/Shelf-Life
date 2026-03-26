"use client";

import { useRef } from "react";

interface CameraViewProps {
  onCapture: (file: File) => void;
}

export function CameraView({ onCapture }: CameraViewProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onCapture(file);
  };

  return (
    <div className="relative w-full aspect-[4/3] bg-accent/90 rounded-2xl overflow-hidden flex items-center justify-center">
      {/* Corner brackets */}
      <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-white/50 rounded-tl" />
      <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-white/50 rounded-tr" />
      <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-white/50 rounded-bl" />
      <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-white/50 rounded-br" />

      {/* Placeholder content (camera will replace this) */}
      <button
        onClick={() => fileInputRef.current?.click()}
        className="flex flex-col items-center gap-2 text-white/70 min-h-0"
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
          <circle cx="8.5" cy="8.5" r="1.5"/>
          <polyline points="21 15 16 10 5 21"/>
        </svg>
        <span className="text-sm font-medium">Tap to upload a photo</span>
      </button>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleFileChange}
        className="hidden"
      />
    </div>
  );
}
