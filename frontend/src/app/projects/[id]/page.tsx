"use client";

import { useEffect, useState, useRef } from "react";
import { useParams } from "next/navigation";
import Navbar from "@/components/Navbar";
import ClipTimeline from "@/components/ClipTimeline";
import {
  fetchProjectDetails,
  triggerAIAnalysis,
  triggerRenderExport,
  fetchJobStatus,
} from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ProjectEditorPage() {
  const params = useParams();
  const projectId = params?.id as string;

  const [projectData, setProjectData] = useState<any>(null);
  const [activeClip, setActiveClip] = useState<any>(null);
  const [activeJob, setActiveJob] = useState<any>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  const loadProject = async () => {
    if (!projectId) return;
    try {
      const data = await fetchProjectDetails(projectId);
      setProjectData(data);
      if (data.clips && data.clips.length > 0 && !activeClip) {
        setActiveClip(data.clips[0]);
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadProject();
  }, [projectId]);

  useEffect(() => {
    if (!activeJob) return;
    const interval = setInterval(async () => {
      try {
        const status = await fetchJobStatus(activeJob.jobId);
        setActiveJob((prev: any) => ({ ...prev, ...status }));
        if (status.status === "completed" || status.status === "failed") {
          clearInterval(interval);
          loadProject();
        }
      } catch (e) {
        console.error(e);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [activeJob?.jobId]);

  const handleStartAnalysis = async () => {
    try {
      const res = await triggerAIAnalysis(projectId);
      setActiveJob({ jobId: res.job_id, type: "analyze", progress: 0, message: "Starting AI highlight analysis..." });
    } catch (e) {
      console.error(e);
    }
  };

  const handleStartRender = async () => {
    try {
      const res = await triggerRenderExport(projectId);
      setActiveJob({ jobId: res.job_id, type: "render_clip", progress: 0, message: "Starting video rendering export..." });
    } catch (e) {
      console.error(e);
    }
  };

  if (!projectData) {
    return (
      <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
        <Navbar />
        <div className="flex-1 flex items-center justify-center">Loading Project...</div>
      </div>
    );
  }

  const { project, clips } = projectData;
  const filename = project.file_path ? project.file_path.split("/").pop() : "source.mp4";
  const sourceVideoUrl = `${API_BASE}/storage/projects/${project.id}/${filename}`;

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
      <Navbar />
      <main className="max-w-7xl mx-auto px-6 py-8 space-y-8 w-full">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">{project.title}</h1>
            <p className="text-sm text-gray-400">
              Duration: {Math.round(project.duration_seconds || 0)}s | Status: {project.status}
            </p>
          </div>
          <div className="flex space-x-4">
            <button
              onClick={handleStartAnalysis}
              className="bg-purple-600 hover:bg-purple-500 text-white font-semibold text-sm px-5 py-2.5 rounded-xl transition"
            >
              🤖 Detect AI Highlights
            </button>
            <button
              onClick={handleStartRender}
              className="bg-pink-600 hover:bg-pink-500 text-white font-semibold text-sm px-5 py-2.5 rounded-xl transition"
            >
              🎬 Render & Export All Clips
            </button>
          </div>
        </div>

        {activeJob && (
          <div className="bg-purple-950/40 border border-purple-800/60 rounded-xl p-5 space-y-2">
            <div className="flex justify-between text-sm font-semibold text-purple-300">
              <span>{activeJob.message || "Processing..."}</span>
              <span>{activeJob.progress || 0}%</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2.5">
              <div
                className="bg-purple-500 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${activeJob.progress || 0}%` }}
              ></div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Player & Active Clip Info */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden aspect-[9/16] relative flex items-center justify-center bg-black">
              <video
                ref={videoRef}
                controls
                className="w-full h-full object-contain"
                src={sourceVideoUrl}
              />
            </div>

            {activeClip && (
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5 space-y-4">
                <h3 className="font-bold text-lg text-purple-400">{activeClip.title}</h3>
                <p className="text-xs text-gray-300"><strong>Hook:</strong> {activeClip.hook}</p>
                <p className="text-xs text-gray-400"><strong>Reason:</strong> {activeClip.reason}</p>
                {activeClip.hashtags && (
                  <div className="flex flex-wrap gap-1">
                    {activeClip.hashtags.map((h: string, i: number) => (
                      <span key={i} className="text-xs bg-gray-800 text-purple-300 px-2 py-0.5 rounded">
                        {h}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Right Column: Timeline & Clip Options */}
          <div className="lg:col-span-2 space-y-6">
            <ClipTimeline
              clips={clips}
              activeClip={activeClip}
              onSelectClip={(c) => {
                setActiveClip(c);
                if (videoRef.current) {
                  videoRef.current.currentTime = c.start_time;
                }
              }}
              onClipsUpdated={loadProject}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
