"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Navbar from "@/components/Navbar";
import UploadZone from "@/components/UploadZone";
import { fetchProjects, fetchJobStatus } from "@/lib/api";

export default function HomePage() {
  const [projects, setProjects] = useState<any[]>([]);
  const [activeJob, setActiveJob] = useState<{ jobId: string; projId: string } | null>(null);
  const [jobStatus, setJobStatus] = useState<any>(null);

  const loadProjects = async () => {
    try {
      const data = await fetchProjects();
      setProjects(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    if (!activeJob) return;
    const interval = setInterval(async () => {
      try {
        const status = await fetchJobStatus(activeJob.jobId);
        setJobStatus(status);
        if (status.status === "completed" || status.status === "failed") {
          clearInterval(interval);
          loadProjects();
        }
      } catch (e) {
        console.error(e);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [activeJob]);

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <Navbar />
      <main className="max-w-6xl mx-auto px-6 py-10 space-y-10">
        <div>
          <h1 className="text-3xl font-extrabold">AI Video Clipper</h1>
          <p className="text-gray-400 mt-1">
            Self-hosted personal creator studio. Import podcasts or streams and automatically generate viral vertical shorts.
          </p>
        </div>

        <UploadZone
          onUploaded={(projId, jobId) => {
            setActiveJob({ projId, jobId });
            loadProjects();
          }}
        />

        {jobStatus && (
          <div className="bg-purple-950/40 border border-purple-800/60 rounded-xl p-5 space-y-2">
            <div className="flex justify-between text-sm font-semibold text-purple-300">
              <span>{jobStatus.message}</span>
              <span>{jobStatus.progress}%</span>
            </div>
            <div className="w-full bg-gray-800 rounded-full h-2.5">
              <div
                className="bg-purple-500 h-2.5 rounded-full transition-all duration-300"
                style={{ width: `${jobStatus.progress}%` }}
              ></div>
            </div>
          </div>
        )}

        <div>
          <h2 className="text-xl font-bold mb-4">Your Projects</h2>
          {projects.length === 0 ? (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center text-gray-400">
              No projects created yet. Upload a video above to start clipping!
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((p) => (
                <Link
                  key={p.id}
                  href={`/projects/${p.id}`}
                  className="bg-gray-900 border border-gray-800 hover:border-purple-500/50 rounded-xl p-5 block transition group"
                >
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="font-bold text-lg text-gray-100 group-hover:text-purple-400 truncate">
                      {p.title}
                    </h3>
                    <span className="text-xs px-2 py-1 bg-gray-800 rounded text-gray-400 uppercase">
                      {p.status}
                    </span>
                  </div>
                  <p className="text-xs text-gray-400">
                    Duration: {Math.round(p.duration_seconds || 0)}s
                  </p>
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(p.created_at).toLocaleDateString()}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
