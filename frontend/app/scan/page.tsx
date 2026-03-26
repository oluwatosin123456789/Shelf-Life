"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { CameraView, ScanButton, StorageSelector } from "@/components/scan";
import { scanFruit, ApiError } from "@/lib/api";

export default function ScanPage() {
  const router = useRouter();
  const [storage, setStorage] = useState("fridge");
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCapture = async (file: File) => {
    setScanning(true);
    setError(null);

    try {
      const result = await scanFruit(file);
      // Store result in sessionStorage for the results page
      sessionStorage.setItem("scanResult", JSON.stringify(result));
      sessionStorage.setItem("scanStorage", storage);
      router.push("/results");
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.detail);
      } else {
        setError("Something went wrong. Please try again.");
      }
      setScanning(false);
    }
  };

  const handleScan = () => {
    const input = document.querySelector<HTMLInputElement>('input[type="file"]');
    input?.click();
  };

  return (
    <div className="flex flex-col px-4 pt-4 pb-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-lg font-semibold">fresco</h1>
        <div className="w-8 h-8 rounded-full bg-border flex items-center justify-center text-xs font-medium">
          U
        </div>
      </div>

      {/* Camera */}
      <CameraView onCapture={handleCapture} />

      {/* Error message (inline, not toast) */}
      {error && (
        <div className="mt-3 p-3 bg-danger/10 border border-danger/20 rounded-xl">
          <p className="text-sm text-danger">{error}</p>
          <button
            onClick={() => setError(null)}
            className="text-xs text-danger/70 underline mt-1 min-h-0"
          >
            Dismiss
          </button>
        </div>
      )}

      {/* Manual select */}
      <p className="text-center text-sm text-text-muted mt-4 mb-6">
        Or select manually
      </p>

      {/* Storage selector */}
      <div className="mb-6">
        <StorageSelector selected={storage} onChange={setStorage} />
      </div>

      {/* Scan button */}
      <div className="flex justify-center">
        <ScanButton onScan={handleScan} loading={scanning} />
      </div>

      {/* Scanning overlay */}
      {scanning && (
        <div className="text-center mt-4">
          <p className="text-sm text-text-muted animate-pulse">Analyzing...</p>
        </div>
      )}
    </div>
  );
}
