"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import { fetchSettings, updateSettings } from "@/lib/api";

export default function SettingsPage() {
  const [settings, setSettings] = useState<any>({
    anthropic_api_key: "",
    openai_api_key: "",
    transcription_engine: "faster-whisper",
    whisper_model_size: "base",
    default_aspect_ratio: "9:16",
    default_caption_style: "yellow_highlight",
    default_watermark_text: "",
  });
  const [statusMsg, setStatusMsg] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings()
      .then((data) => setSettings(data))
      .catch((e) => console.error(e));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updated = await updateSettings(settings);
      setSettings(updated);
      setStatusMsg("Settings saved successfully!");
      setTimeout(() => setStatusMsg(null), 3000);
    } catch (e: any) {
      setStatusMsg(`Error: ${e.message}`);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 flex flex-col">
      <Navbar />
      <main className="max-w-4xl mx-auto px-6 py-10 space-y-8 w-full">
        <div>
          <h1 className="text-3xl font-extrabold">App Settings</h1>
          <p className="text-gray-400 mt-1">
            Configure your local self-hosted API keys and default clip rendering preferences.
          </p>
        </div>

        {statusMsg && (
          <div className="bg-purple-950/60 border border-purple-700 text-purple-200 px-4 py-3 rounded-xl text-sm">
            {statusMsg}
          </div>
        )}

        <form onSubmit={handleSave} className="bg-gray-900 border border-gray-800 rounded-2xl p-8 space-y-6">
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-purple-400 border-b border-gray-800 pb-2">API Keys</h2>
            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">
                Anthropic API Key (Claude) - Local Env Only
              </label>
              <input
                type="password"
                placeholder="sk-ant-..."
                value={settings.anthropic_api_key || ""}
                onChange={(e) => setSettings({ ...settings, anthropic_api_key: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm text-gray-200 focus:outline-none focus:border-purple-500 font-mono"
              />
              <p className="text-xs text-gray-500 mt-1">
                Used strictly for AI Highlight Detection & SEO Metadata generation.
              </p>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">
                OpenAI API Key (Optional Whisper API)
              </label>
              <input
                type="password"
                placeholder="sk-..."
                value={settings.openai_api_key || ""}
                onChange={(e) => setSettings({ ...settings, openai_api_key: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm text-gray-200 focus:outline-none focus:border-purple-500 font-mono"
              />
            </div>
          </div>

          <div className="space-y-4 pt-4">
            <h2 className="text-lg font-bold text-purple-400 border-b border-gray-800 pb-2">
              Transcription & Video Defaults
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1">Transcription Engine</label>
                <select
                  value={settings.transcription_engine || "faster-whisper"}
                  onChange={(e) => setSettings({ ...settings, transcription_engine: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="faster-whisper">Faster-Whisper (Local Offline Free)</option>
                  <option value="openai-whisper">OpenAI Whisper API</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1">Default Aspect Ratio</label>
                <select
                  value={settings.default_aspect_ratio || "9:16"}
                  onChange={(e) => setSettings({ ...settings, default_aspect_ratio: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="9:16">9:16 (TikTok / Reels / Shorts Vertical)</option>
                  <option value="1:1">1:1 (Instagram Square)</option>
                  <option value="16:9">16:9 (YouTube Landscape)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1">Default Caption Style</label>
                <select
                  value={settings.default_caption_style || "yellow_highlight"}
                  onChange={(e) => setSettings({ ...settings, default_caption_style: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
                >
                  <option value="yellow_highlight">Yellow Highlight Center</option>
                  <option value="bold_center">Bold White Center</option>
                  <option value="minimal_bottom">Minimal Bottom Subtitle</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-400 mb-1">Default Watermark Text</label>
                <input
                  type="text"
                  placeholder="@mychannel"
                  value={settings.default_watermark_text || ""}
                  onChange={(e) => setSettings({ ...settings, default_watermark_text: e.target.value })}
                  className="w-full bg-gray-800 border border-gray-700 rounded-lg p-3 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-4">
            <button
              type="submit"
              className="bg-purple-600 hover:bg-purple-500 text-white font-semibold text-sm px-6 py-3 rounded-xl transition"
            >
              Save Settings
            </button>
          </div>
        </form>
      </main>
    </div>
  );
}
