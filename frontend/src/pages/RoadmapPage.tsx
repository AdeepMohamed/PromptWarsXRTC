import React, { useEffect, useState } from "react";
import {
  Map,
  CheckCircle2,
  Clock,
  ExternalLink,
  Code2,
  AlertTriangle,
  PlayCircle,
  Sparkles,
  BookOpen,
  BrainCircuit,
  Filter,
} from "lucide-react";
import api from "../lib/api";

export function RoadmapPage() {
  const [roadmap, setRoadmap] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTask, setSelectedTask] = useState<any>(null);
  const [updatingTaskId, setUpdatingTaskId] = useState<string | null>(null);

  const fetchRoadmap = async () => {
    try {
      const res = await api.get("/roadmap");
      setRoadmap(res.data.roadmap);
      if (res.data.roadmap?.tasks?.length > 0 && !selectedTask) {
        setSelectedTask(res.data.roadmap.tasks[0]);
      }
    } catch (err) {
      console.error("Failed to load roadmap:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRoadmap();
  }, []);

  const handleUpdateStatus = async (taskId: string, newStatus: string) => {
    setUpdatingTaskId(taskId);
    try {
      await api.put(`/roadmap/tasks/${taskId}`, { status: newStatus });
      await fetchRoadmap();
      if (selectedTask?.id === taskId) {
        setSelectedTask((prev: any) => ({ ...prev, status: newStatus }));
      }
    } catch (err) {
      console.error("Failed to update task status:", err);
    } finally {
      setUpdatingTaskId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Loading Adaptive Learning Roadmap...</p>
        </div>
      </div>
    );
  }

  // Group tasks by week
  const tasks = roadmap?.tasks || [];
  const weeksMap: { [week: number]: any[] } = {};
  for (const t of tasks) {
    const wk = t.week_number || 1;
    if (!weeksMap[wk]) weeksMap[wk] = [];
    weeksMap[wk].push(t);
  }
  const weekNumbers = Object.keys(weeksMap).map(Number).sort((a, b) => a - b);

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
            <Map className="w-3.5 h-3.5" />
            <span>Autonomous Self-Adapting Curriculum</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">{roadmap?.title || "Career Roadmap"}</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Total Estimated Effort: <strong className="text-slate-800">{roadmap?.total_estimated_hours || 0} Hours</strong> across {weekNumbers.length} Structured Weeks.
          </p>
        </div>
      </div>

      {/* Main Layout: Weeks Timeline (7 cols) + Task Detail Inspector (5 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Timeline (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          {weekNumbers.length === 0 ? (
            <div className="p-8 rounded-2xl bg-white border border-slate-200 text-center text-xs text-slate-500">
              No roadmap generated yet. Complete onboarding or run Initial Analysis.
            </div>
          ) : (
            weekNumbers.map((wk) => {
              const weekTasks = weeksMap[wk];
              const completedCount = weekTasks.filter((t) => t.status === "completed").length;

              return (
                <div key={wk} className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
                  {/* Week Title & Progress */}
                  <div className="flex items-center justify-between mb-4 pb-3 border-b border-slate-100">
                    <div className="flex items-center gap-2">
                      <span className="w-7 h-7 rounded-lg bg-violet-600 text-white font-bold text-xs flex items-center justify-center">
                        {wk}
                      </span>
                      <h3 className="font-bold text-sm text-slate-900">Week {wk} Curriculum</h3>
                    </div>
                    <span className="text-xs font-medium text-slate-500">
                      {completedCount} of {weekTasks.length} Completed
                    </span>
                  </div>

                  {/* Tasks List */}
                  <div className="space-y-3">
                    {weekTasks.map((t) => {
                      const isSelected = selectedTask?.id === t.id;
                      const isCompleted = t.status === "completed";
                      const isIntervention = t.title.startsWith("[Intervention]");

                      return (
                        <div
                          key={t.id}
                          onClick={() => setSelectedTask(t)}
                          className={`p-4 rounded-xl border transition cursor-pointer flex items-center justify-between gap-3 ${
                            isSelected
                              ? "border-violet-500 bg-violet-50/50 shadow-sm"
                              : isIntervention
                              ? "border-amber-300 bg-amber-50/50 hover:border-amber-400"
                              : "border-slate-100 hover:border-slate-200 bg-slate-50/60"
                          }`}
                        >
                          <div className="min-w-0 flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              {isIntervention && (
                                <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-amber-200 text-amber-900 uppercase">
                                  Remedial Intervention
                                </span>
                              )}
                              <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-slate-200 text-slate-700">
                                {t.difficulty || "Beginner"}
                              </span>
                            </div>
                            <h4 className="text-sm font-bold text-slate-900 truncate">{t.title}</h4>
                            <p className="text-xs text-slate-500 line-clamp-1">{t.description}</p>
                          </div>

                          <div className="flex items-center gap-2 shrink-0">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleUpdateStatus(t.id, isCompleted ? "pending" : "completed");
                              }}
                              disabled={updatingTaskId === t.id}
                              className={`p-2 rounded-xl transition ${
                                isCompleted
                                  ? "bg-emerald-100 text-emerald-700 hover:bg-emerald-200"
                                  : "bg-slate-200 text-slate-500 hover:bg-violet-100 hover:text-violet-700"
                              }`}
                              title={isCompleted ? "Mark Pending" : "Mark Completed"}
                            >
                              <CheckCircle2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Task Inspector (5 cols) */}
        <div className="lg:col-span-5">
          <div className="sticky top-8 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-5">
            {selectedTask ? (
              <>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-violet-100 text-violet-700">
                      Week {selectedTask.week_number} Task
                    </span>
                    <span className="text-xs font-semibold capitalize text-slate-600">
                      Status: {selectedTask.status}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900">{selectedTask.title}</h3>
                  <p className="text-xs text-slate-600 mt-1">{selectedTask.description}</p>
                </div>

                <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 space-y-2 text-xs">
                  <div>
                    <span className="font-bold text-slate-700">Learning Objective:</span>
                    <p className="text-slate-600 mt-0.5">{selectedTask.learning_objective || "Master essential patterns and concepts."}</p>
                  </div>
                  <div>
                    <span className="font-bold text-slate-700">Completion Criteria:</span>
                    <p className="text-slate-600 mt-0.5">{selectedTask.completion_criteria || "Complete practice coding and verify understanding."}</p>
                  </div>
                </div>

                {selectedTask.practical_exercise && (
                  <div className="p-3.5 rounded-xl bg-violet-50/60 border border-violet-100 text-xs">
                    <span className="font-bold text-violet-900 flex items-center gap-1.5 mb-1">
                      <Code2 className="w-3.5 h-3.5" /> Practical Code Exercise
                    </span>
                    <p className="text-violet-800">{selectedTask.practical_exercise}</p>
                  </div>
                )}

                {selectedTask.recommended_resource && (
                  <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-100 text-xs">
                    <span className="font-bold text-slate-700 flex items-center gap-1.5 mb-1">
                      <BookOpen className="w-3.5 h-3.5" /> Recommended Resource
                    </span>
                    <p className="text-slate-600">{selectedTask.recommended_resource}</p>
                  </div>
                )}

                {/* Status Toggle Action */}
                <div className="pt-4 border-t border-slate-100">
                  <button
                    onClick={() =>
                      handleUpdateStatus(
                        selectedTask.id,
                        selectedTask.status === "completed" ? "pending" : "completed"
                      )
                    }
                    disabled={updatingTaskId === selectedTask.id}
                    className={`w-full py-2.5 rounded-xl text-xs font-semibold transition flex items-center justify-center gap-2 ${
                      selectedTask.status === "completed"
                        ? "bg-slate-100 text-slate-700 hover:bg-slate-200"
                        : "bg-emerald-600 hover:bg-emerald-500 text-white shadow-md shadow-emerald-600/20"
                    }`}
                  >
                    <CheckCircle2 className="w-4 h-4" />
                    {selectedTask.status === "completed" ? "Mark as Incomplete" : "Mark as Completed"}
                  </button>
                </div>
              </>
            ) : (
              <div className="text-center py-12 text-xs text-slate-400">
                Select a roadmap task on the left to inspect learning objectives and code exercises.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
