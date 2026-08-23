const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchProjects() {
  const res = await fetch(`${API_BASE}/api/projects`);
  if (!res.ok) throw new Error("Failed to fetch projects");
  return res.json();
}

export async function fetchProjectDetails(id: string) {
  const res = await fetch(`${API_BASE}/api/projects/${id}`);
  if (!res.ok) throw new Error("Failed to fetch project");
  return res.json();
}

export async function uploadVideo(file: File, title?: string) {
  const formData = new FormData();
  formData.append("file", file);
  if (title) formData.append("title", title);

  const res = await fetch(`${API_BASE}/api/projects/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) throw new Error("Upload failed");
  return res.json();
}

export async function fetchJobStatus(jobId: string) {
  const res = await fetch(`${API_BASE}/api/jobs/${jobId}`);
  if (!res.ok) throw new Error("Failed to fetch job status");
  return res.json();
}

export async function triggerAIAnalysis(projectId: string) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/analyze`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to start AI analysis");
  return res.json();
}

export async function triggerRenderExport(projectId: string) {
  const res = await fetch(`${API_BASE}/api/projects/${projectId}/render`, {
    method: "POST",
  });
  if (!res.ok) throw new Error("Failed to start render export");
  return res.json();
}

export async function updateClip(clipId: string, payload: any) {
  const res = await fetch(`${API_BASE}/api/projects/clips/${clipId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Failed to update clip");
  return res.json();
}

export async function fetchSettings() {
  const res = await fetch(`${API_BASE}/api/settings`);
  if (!res.ok) throw new Error("Failed to fetch settings");
  return res.json();
}

export async function updateSettings(settings: any) {
  const res = await fetch(`${API_BASE}/api/settings`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(settings),
  });
  if (!res.ok) throw new Error("Failed to update settings");
  return res.json();
}
