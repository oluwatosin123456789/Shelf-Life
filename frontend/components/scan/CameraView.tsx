"use client";

import { useRef, useState, useEffect, useCallback } from "react";

interface CameraViewProps {
  /** Called when the user captures or selects an image */
  onCapture: (file: File) => void;
  /** If true, disable controls (scanning in progress) */
  disabled?: boolean;
}

type Mode = "camera" | "upload";

export function CameraView({ onCapture, disabled = false }: CameraViewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const [mode, setMode] = useState<Mode>("camera");
  const [cameraReady, setCameraReady] = useState(false);
  const [cameraError, setCameraError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [capturedFile, setCapturedFile] = useState<File | null>(null);

  // --------------------------------------------------
  // Start / stop camera
  // --------------------------------------------------
  const startCamera = useCallback(async () => {
    setCameraError(null);
    setCameraReady(false);

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 1280 }, height: { ideal: 960 } },
        audio: false,
      });

      streamRef.current = stream;

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.onloadedmetadata = () => {
          videoRef.current?.play();
          setCameraReady(true);
        };
      }
    } catch (err: unknown) {
      const msg =
        err instanceof DOMException && err.name === "NotAllowedError"
          ? "Camera permission denied. Use 'Upload' instead."
          : "Camera not available. Use 'Upload' instead.";
      setCameraError(msg);
      setMode("upload");
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((t) => t.stop());
      streamRef.current = null;
    }
    setCameraReady(false);
  }, []);

  // Auto-start/stop when mode changes
  useEffect(() => {
    if (mode === "camera" && !preview) {
      startCamera();
    } else {
      stopCamera();
    }
    return () => stopCamera();
  }, [mode, preview, startCamera, stopCamera]);

  // --------------------------------------------------
  // Capture from live feed
  // --------------------------------------------------
  const captureFrame = () => {
    const video = videoRef.current;
    const canvas = canvasRef.current;
    if (!video || !canvas) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.drawImage(video, 0, 0);

    canvas.toBlob(
      (blob) => {
        if (!blob) return;
        const file = new File([blob], "scan.jpg", { type: "image/jpeg" });
        setPreview(URL.createObjectURL(blob));
        setCapturedFile(file);
        stopCamera();
      },
      "image/jpeg",
      0.92,
    );
  };

  // --------------------------------------------------
  // File upload handler
  // --------------------------------------------------
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setPreview(URL.createObjectURL(file));
    setCapturedFile(file);
  };

  // --------------------------------------------------
  // Confirm (sends file to parent)
  // --------------------------------------------------
  const confirmCapture = () => {
    if (capturedFile) {
      onCapture(capturedFile);
    }
  };

  // --------------------------------------------------
  // Retake / reset
  // --------------------------------------------------
  const retake = () => {
    setPreview(null);
    setCapturedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
    if (mode === "camera") startCamera();
  };

  // --------------------------------------------------
  // Render
  // --------------------------------------------------
  return (
    <div className="flex flex-col gap-3">
      {/* -------- Viewfinder -------- */}
      <div className="relative w-full aspect-[4/3] bg-zinc-900 rounded-2xl overflow-hidden flex items-center justify-center">
        {/* Corner brackets */}
        <div className="absolute top-4 left-4 w-6 h-6 border-t-2 border-l-2 border-white/40 rounded-tl z-10" />
        <div className="absolute top-4 right-4 w-6 h-6 border-t-2 border-r-2 border-white/40 rounded-tr z-10" />
        <div className="absolute bottom-4 left-4 w-6 h-6 border-b-2 border-l-2 border-white/40 rounded-bl z-10" />
        <div className="absolute bottom-4 right-4 w-6 h-6 border-b-2 border-r-2 border-white/40 rounded-br z-10" />

        {/* Captured preview */}
        {preview && (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={preview} alt="Captured" className="absolute inset-0 w-full h-full object-cover" />
        )}

        {/* Live camera feed */}
        {!preview && mode === "camera" && (
          <>
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className={`absolute inset-0 w-full h-full object-cover transition-opacity duration-300 ${cameraReady ? "opacity-100" : "opacity-0"}`}
            />
            {!cameraReady && !cameraError && (
              <div className="flex flex-col items-center gap-2 text-white/60">
                <span className="h-6 w-6 rounded-full border-2 border-white/40 border-t-transparent animate-spin" />
                <span className="text-xs">Starting camera…</span>
              </div>
            )}
          </>
        )}

        {/* Upload prompt */}
        {!preview && mode === "upload" && (
          <button
            onClick={() => fileInputRef.current?.click()}
            className="flex flex-col items-center gap-2 text-white/70 min-h-0 p-4"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            <span className="text-sm font-medium">Tap to upload a photo</span>
          </button>
        )}

        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          capture="environment"
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Off-screen canvas for frame capture */}
        <canvas ref={canvasRef} className="hidden" />
      </div>

      {/* -------- Controls -------- */}
      <div className="flex items-center justify-between">
        {/* Mode toggle */}
        <div className="flex bg-surface rounded-xl p-1 gap-1">
          <button
            onClick={() => { if (!disabled) { setPreview(null); setCapturedFile(null); setMode("camera"); } }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors min-h-0 ${
              mode === "camera" ? "bg-accent text-white" : "text-text-muted hover:text-text"
            }`}
            disabled={disabled}
          >
            📷 Camera
          </button>
          <button
            onClick={() => { if (!disabled) { setPreview(null); setCapturedFile(null); setMode("upload"); } }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors min-h-0 ${
              mode === "upload" ? "bg-accent text-white" : "text-text-muted hover:text-text"
            }`}
            disabled={disabled}
          >
            📁 Upload
          </button>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2">
          {preview && !disabled && (
            <button
              onClick={retake}
              className="px-4 py-1.5 rounded-xl bg-surface text-xs font-medium text-text-muted hover:text-text transition-colors min-h-0"
            >
              Retake
            </button>
          )}

          {/* Shutter button — only when camera is live and no preview */}
          {!preview && mode === "camera" && cameraReady && !disabled && (
            <button
              onClick={captureFrame}
              className="w-14 h-14 rounded-full border-[3px] border-white bg-white/20 hover:bg-white/40 active:scale-90 transition-all min-h-0 flex items-center justify-center"
              aria-label="Capture photo"
            >
              <div className="w-10 h-10 rounded-full bg-white/90" />
            </button>
          )}
        </div>
      </div>

      {/* -------- Scan / Confirm button -------- */}
      {preview && capturedFile && !disabled && (
        <button
          onClick={confirmCapture}
          className="w-full py-3 rounded-2xl bg-accent text-white font-semibold text-sm hover:bg-accent/90 active:scale-[0.98] transition-all min-h-0"
        >
          🔍 Scan This Fruit
        </button>
      )}

      {/* Camera error */}
      {cameraError && (
        <p className="text-xs text-amber-400 text-center">{cameraError}</p>
      )}
    </div>
  );
}
