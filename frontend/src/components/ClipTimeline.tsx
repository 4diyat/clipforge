"use client";

import { useState } from "react";
import { updateClip } from "@/lib/api";

export default function ClipTimeline({
  clips,
  activeClip,
  onSelectClip,
  onClipsUpdated,
}: {
  clips: any[];
  activeClip: any;
  onSelectClip: (clip: any) => void;
  onClipsUpdated: () => void;
}) {
  const [editingClip, setEditingClip] = useState<any>(activeClip);

  if (!clips || clips.length === 0) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 text-center text-gray-400">
        No AI clips detected yet. Run AI Analysis to generate clip highlights!
      </div>
    );
  }

  const handleSaveSettings = async () => {
    if (!editingClip) return;
    try {
      await updateClip(editingClip.id, {
        aspect_ratio: editingClip.aspect_ratio,
        caption_style: editingClip.caption_style,
        word_level_highlight: editingClip.word_level_highlight,
        watermark_text: editingClip.watermark_text,
        start_time: parseFloat(editingClip.start_time),
        end_time: parseFloat(editingClip.end_time),
      });
      onClipsUpdated();
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="space-y-6">
      {/* Clip List Carousel / Timeline Markers */}
      <div className="space-y-2">
        <h3 className="font-bold text-lg text-gray-200">AI Highlight Clips ({clips.length})</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {clips.map((clip) => {
            const isSelected = activeClip?.id === clip.id;
            return (
              <div
                key={clip.id}
                onClick={() => {
                  onSelectClip(clip);
                  setEditingClip(clip);
                }}
                className={`p-4 rounded-xl border cursor-pointer transition ${
                  isSelected
                    ? "bg-purple-900/30 border-purple-500"
                    : "bg-gray-900 border-gray-800 hover:border-gray-700"
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <span className="font-bold text-sm text-purple-300 truncate">{clip.title}</span>
                  <span className="text-xs bg-purple-950 text-purple-400 px-2 py-0.5 rounded font-mono">
                    🔥 {clip.virality_score}%
                  </span>
                </div>
                <p className="text-xs text-gray-400 line-clamp-2 mt-1">{clip.hook}</p>
                <div className="flex justify-between items-center text-xs text-gray-500 mt-3 font-mono">
                  <span>
                    {clip.start_time.toFixed(1)}s - {clip.end_time.toFixed(1)}s
                  </span>
                  <span>{(clip.end_time - clip.start_time).toFixed(1)}s</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Editor Controls for Selected Clip */}
      {editingClip && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-6">
          <h4 className="font-bold text-md text-purple-400 border-b border-gray-800 pb-2">
            Clip Settings & Reframing Options
          </h4>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Target Aspect Ratio</label>
              <select
                value={editingClip.aspect_ratio || "9:16"}
                onChange={(e) => setEditingClip({ ...editingClip, aspect_ratio: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg p-2.5 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
              >
                <option value="9:16">9:16 (TikTok / Reels / Shorts Vertical)</option>
                <option value="1:1">1:1 (Instagram Feed Square)</option>
                <option value="16:9">16:9 (YouTube Landscape)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Caption Visual Style</label>
              <select
                value={editingClip.caption_style || "yellow_highlight"}
                onChange={(e) => setEditingClip({ ...editingClip, caption_style: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg p-2.5 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
              >
                <option value="yellow_highlight">Yellow Highlight Center (Viral Pop)</option>
                <option value="bold_center">Bold White Center</option>
                <option value="minimal_bottom">Minimal Bottom Subtitle</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Trim Start Time (seconds)</label>
              <input
                type="number"
                step="0.1"
                value={editingClip.start_time}
                onChange={(e) => setEditingClip({ ...editingClip, start_time: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg p-2.5 text-sm text-gray-200 focus:outline-none focus:border-purple-500 font-mono"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 mb-1">Trim End Time (seconds)</label>
              <input
                type="number"
                step="0.1"
                value={editingClip.end_time}
                onChange={(e) => setEditingClip({ ...editingClip, end_time: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg p-2.5 text-sm text-gray-200 focus:outline-none focus:border-purple-500 font-mono"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-xs font-semibold text-gray-400 mb-1">Watermark Overlay Text</label>
              <input
                type="text"
                placeholder="@mychannel"
                value={editingClip.watermark_text || ""}
                onChange={(e) => setEditingClip({ ...editingClip, watermark_text: e.target.value })}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg p-2.5 text-sm text-gray-200 focus:outline-none focus:border-purple-500"
              />
            </div>
          </div>

          <div className="flex justify-end pt-2">
            <button
              onClick={handleSaveSettings}
              className="bg-purple-600 hover:bg-purple-500 text-white font-semibold text-sm px-5 py-2.5 rounded-lg transition"
            >
              Save Clip Adjustments
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
