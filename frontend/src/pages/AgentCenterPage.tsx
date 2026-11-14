import React, { useEffect, useState } from "react";
import { Activity, RefreshCw, Filter, Clock, CheckCircle2, AlertTriangle, ChevronDown, ChevronUp, BrainCircuit } from "lucide-react";
import api from "../lib/api";

export function AgentCenterPage() {
  const [activities, setActivities] = useState<any[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>("all");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchActivities = async () => {
    try {
      const res = await api.get("/agents/activity?limit=100");
      setActivities(res.data.activities || []);
    } catch (err) {
      console.error("Failed to load agent activities:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchActivities();
  }, []);

  const handleRefresh = () => {
    setRefreshing(true);
    fetchActivities();
  };

  const filtered = activities.filter((act) => {
    if (selectedAgent === "all") return true;
    return act.agent_name === selectedAgent;
  });

  const toggleExpand = (id: string) => {
    setExpandedId((prev) => (prev === id ? null : id));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Connecting to Agent Execution Telemetry...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
            <Activity className="w-3.5 h-3.5" />
            <span>Observable Distributed Telemetry</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Agent Activity Center</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time backend logs of the 5 specialized AI agents persisted directly in Neon PostgreSQL.
          </p>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 shadow-sm transition self-start sm:self-auto disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refreshing ? "animate-spin" : ""}`} /> Refresh Telemetry
        </button>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center gap-2">
        <span className="text-xs font-semibold text-slate-500 mr-2 flex items-center gap-1">
          <Filter className="w-3.5 h-3.5" /> Filter Agent:
        </span>
        {[
          { label: "All Agents", val: "all" },
          { label: "Skill Agent", val: "skill_agent" },
          { label: "Career Agent", val: "career_agent" },
          { label: "Learning Agent", val: "learning_agent" },
          { label: "Performance Agent", val: "performance_agent" },
          { label: "Mentor Agent", val: "mentor_agent" },
        ].map((item) => (
          <button
            key={item.val}
            onClick={() => setSelectedAgent(item.val)}
            className={`px-3 py-1.5 rounded-xl text-xs font-medium transition ${
              selectedAgent === item.val
                ? "bg-slate-900 text-white shadow-sm"
                : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
            }`}
          >
            {item.label}
          </button>
        ))}
      </div>

      {/* Events List */}
      <div className="space-y-3">
        {filtered.length === 0 ? (
          <div className="p-12 rounded-3xl bg-white border border-slate-200 text-center text-xs text-slate-500">
            No agent activities found for the selected filter.
          </div>
        ) : (
          filtered.map((act) => {
            const isExpanded = expandedId === act.id;
            const isCompleted = act.status === "completed";
            const isFailed = act.status === "failed";

            return (
              <div
                key={act.id}
                className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm transition hover:border-slate-300"
              >
                <div
                  className="flex items-center justify-between cursor-pointer select-none"
                  onClick={() => toggleExpand(act.id)}
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span
                      className={`w-2.5 h-2.5 rounded-full shrink-0 ${
                        isCompleted ? "bg-emerald-500" : isFailed ? "bg-red-500" : "bg-amber-500 animate-pulse"
                      }`}
                    ></span>

                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-sm text-slate-900 capitalize">
                          {act.agent_name.replace("_", " ")}
                        </span>
                        <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-slate-100 text-slate-600">
                          {act.task}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400 mt-0.5">
                        {act.started_at ? new Date(act.started_at).toLocaleString() : "Just now"}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-xs font-mono text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3 text-slate-400" /> {act.duration_ms}ms
                    </span>
                    <span
                      className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${
                        isCompleted
                          ? "bg-emerald-100 text-emerald-800"
                          : isFailed
                          ? "bg-red-100 text-red-800"
                          : "bg-amber-100 text-amber-800"
                      }`}
                    >
                      {act.status}
                    </span>
                    <button className="text-slate-400 hover:text-slate-600">
                      {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </button>
                  </div>
                </div>

                {/* Expanded Payload Inspector */}
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-slate-100 space-y-3 text-xs">
                    <div>
                      <span className="font-bold text-slate-600 uppercase text-[10px] tracking-wider block mb-1">
                        Input Summary:
                      </span>
                      <pre className="p-3 rounded-xl bg-slate-950 text-slate-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap">
                        {act.input_summary || "{}"}
                      </pre>
                    </div>

                    <div>
                      <span className="font-bold text-slate-600 uppercase text-[10px] tracking-wider block mb-1">
                        Output Summary / Result:
                      </span>
                      <pre className="p-3 rounded-xl bg-slate-950 text-slate-300 font-mono text-[11px] overflow-x-auto whitespace-pre-wrap">
                        {act.output_summary || "{}"}
                      </pre>
                    </div>

                    {act.error_message && (
                      <div>
                        <span className="font-bold text-red-600 uppercase text-[10px] tracking-wider block mb-1">
                          Exception Log:
                        </span>
                        <div className="p-3 rounded-xl bg-red-950/40 border border-red-800/50 text-red-300 font-mono text-[11px]">
                          {act.error_message}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
