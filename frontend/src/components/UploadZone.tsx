"use client";

import { useState } from "react";
import { uploadVideo } from "@/lib/api";

export default function UploadZone({ onUploaded }: { onUploaded: (projId: string, jobId: string) => void }) {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 2 * 1024 * 1024 * 1024) {
      setError("Warning: Video file is over 2GB. Processing may take longer.");
    } else {
      setError(null);
    }

    setIsUploading(true);
    try {
      const res = await uploadVideo(file);
      onUploaded(res.project_id, res.job_id);
    } catch (err: any) {
      setError(err.message || "Failed to upload video");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="border-2 border-dashed border-gray-700 hover:border-purple-500 rounded-2xl p-10 text-center bg-gray-900/50 transition cursor-pointer">
      <input
        type="file"
        accept="video/mp4,video/quicktime,video/x-matroska"
        className="hidden"
        id="video-file-input"
        onChange={handleFileChange}
        disabled={isUploading}
      />
      <label htmlFor="video-file-input" className="cursor-pointer block">
        <div className="text-5xl mb-4">📹</div>
        <p className="text-lg font-semibold text-gray-200">
          {isUploading ? "Uploading Video File..." : "Click or Drag & Drop Long Video File"}
        </p>
        <p className="text-sm text-gray-400 mt-2">
          Supports MP4, MOV, MKV (Podcasts, Streams, Vlogs) up to 2GB
        </p>
      </label>
      {error && <p className="mt-4 text-sm text-amber-400 font-medium">{error}</p>}
    </div>
  );
}
