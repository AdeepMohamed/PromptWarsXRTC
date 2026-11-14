import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  Sparkles,
  Target,
  CheckCircle2,
  AlertTriangle,
  Clock,
  ArrowUpRight,
  TrendingUp,
  BrainCircuit,
  ClipboardCheck,
  Map,
  Compass,
  ArrowRight,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
} from "recharts";
import api from "../lib/api";

export function DashboardPage() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [orchestrating, setOrchestrating] = useState(false);

  const fetchDashboard = async () => {
    try {
      const res = await api.get("/analytics/dashboard");
      setData(res.data.dashboard);
    } catch (err) {
      console.error("Failed to load dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleRunOrchestration = async () => {
    setOrchestrating(true);
    try {
      await api.post("/agents/orchestrate", {
        workflow: "initial_analysis",
        params: {},
      });
      await fetchDashboard();
    } catch (err) {
      console.error("Orchestration failed:", err);
    } finally {
      setOrchestrating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-12 h-12 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-6 h-6" />
          </div>
          <p className="text-sm font-medium text-slate-600">Loading Career Intelligence Command Center...</p>
        </div>
      </div>
    );
  }

  const readiness = Number(data?.career_readiness || 0);

  return (
    <div className="space-y-8 pb-12">
      {/* Top Banner / Welcome */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white shadow-xl">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-violet-500/20 border border-violet-500/30 text-violet-300 text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Agentic Career Intelligence Active</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight">
            Target Goal: {data?.current_career_goal || "Full Stack Developer"}
          </h1>
          <p className="text-xs text-slate-300 mt-1 max-w-xl">
            Continuously evaluated across 5 collaborating AI agents, real-time diagnostic performance, and Neon PostgreSQL competency benchmarks.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <Link
            to="/careers"
            className="px-4 py-2 rounded-xl text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition"
          >
            Change Goal
          </Link>
          <button
            onClick={handleRunOrchestration}
            disabled={orchestrating}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-md shadow-violet-600/30 transition flex items-center gap-2 disabled:opacity-50"
          >
            <BrainCircuit className="w-3.5 h-3.5" />
            {orchestrating ? "Orchestrating..." : "Sync Agent Analysis"}
          </button>
        </div>
      </div>

      {/* Primary KPI Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Career Readiness */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Career Readiness</span>
            <span className="p-2 rounded-xl bg-violet-50 text-violet-600">
              <Target className="w-4 h-4" />
            </span>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">
              {readiness.toFixed(1)}%
            </div>
            <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden mb-2">
              <div
                className="bg-gradient-to-r from-violet-600 to-indigo-600 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(readiness, 100)}%` }}
              ></div>
            </div>
            <p className="text-[11px] text-slate-400 font-medium">
              *Estimated readiness metric based on weighted competency proficiencies; not an employment guarantee.
            </p>
          </div>
        </div>

        {/* Learning Progress */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Roadmap Progress</span>
            <span className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
              <Map className="w-4 h-4" />
            </span>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-slate-900 tracking-tight mb-2">
              {data?.learning_progress || 0}%
            </div>
            <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden mb-2">
              <div
                className="bg-indigo-600 h-full rounded-full transition-all duration-500"
                style={{ width: `${data?.learning_progress || 0}%` }}
              ></div>
            </div>
            <p className="text-[11px] text-slate-500">
              Personalized 6-week curriculum generated by Learning Agent.
            </p>
          </div>
        </div>

        {/* Skills Mastered */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Skills Mastered</span>
            <span className="p-2 rounded-xl bg-emerald-50 text-emerald-600">
              <CheckCircle2 className="w-4 h-4" />
            </span>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-slate-900 tracking-tight mb-1">
              {data?.skills_mastered || 0} <span className="text-sm font-normal text-slate-500">/ {data?.total_skills || 0}</span>
            </div>
            <p className="text-xs text-emerald-700 font-medium flex items-center gap-1 mt-2">
              <TrendingUp className="w-3.5 h-3.5" /> High proficiency verified
            </p>
          </div>
        </div>

        {/* Missing Competencies */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Missing Competencies</span>
            <span className="p-2 rounded-xl bg-amber-50 text-amber-600">
              <AlertTriangle className="w-4 h-4" />
            </span>
          </div>
          <div>
            <div className="text-3xl font-extrabold text-slate-900 tracking-tight mb-1">
              {data?.missing_skills?.length || 0}
            </div>
            <p className="text-xs text-amber-700 font-medium mt-2">
              Priority gaps to bridge for role readiness
            </p>
          </div>
        </div>
      </div>

      {/* Main Grid: Upcoming Tasks & Weekly Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Next Learning Tasks (2 Cols) */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-base font-bold text-slate-900">Upcoming Learning Tasks</h2>
              <p className="text-xs text-slate-500">Adaptive curriculum synthesized by Learning Agent</p>
            </div>
            <Link to="/roadmap" className="text-xs font-semibold text-violet-600 hover:text-violet-700 flex items-center gap-1">
              View Full Roadmap <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-3">
            {(data?.upcoming_tasks || []).length === 0 ? (
              <div className="text-center py-8 text-xs text-slate-500">
                No active tasks pending. Run initial analysis to generate your roadmap!
              </div>
            ) : (
              (data?.upcoming_tasks || []).map((t: any) => (
                <div
                  key={t.id}
                  className="p-4 rounded-xl border border-slate-100 hover:border-slate-200 bg-slate-50/60 transition flex items-center justify-between"
                >
                  <div className="flex items-start gap-3 min-w-0">
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-violet-100 text-violet-700 shrink-0 mt-0.5">
                      Wk {t.week_number}
                    </span>
                    <div className="min-w-0">
                      <h4 className="text-sm font-semibold text-slate-800 truncate">{t.title}</h4>
                      <p className="text-xs text-slate-500 line-clamp-1">{t.learning_objective || t.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5" /> {t.estimated_hours}h
                    </span>
                    <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-200 text-slate-700 uppercase">
                      {t.status}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Weekly Activity (1 Col) */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-base font-bold text-slate-900">Weekly Activity</h2>
                <p className="text-xs text-slate-500">Learning hours logged per day</p>
              </div>
            </div>
            <div className="h-44 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data?.weekly_activity || []}>
                  <XAxis dataKey="day" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Bar dataKey="hours" fill="#7c3aed" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
          <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Weekly Target: 20 Hours</span>
            <span className="font-semibold text-slate-800">
              {(data?.weekly_activity || []).reduce((acc: number, curr: any) => acc + (curr.hours || 0), 0)} Hours Completed
            </span>
          </div>
        </div>
      </div>

      {/* Second Grid: AI Recommendations & Recent Agent Events */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Personalized AI Recommendations */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Personalized AI Recommendations</h2>
              <p className="text-xs text-slate-500">Strategized from your active skill DNA and gaps</p>
            </div>
            <span className="p-1.5 rounded-lg bg-violet-50 text-violet-600">
              <Sparkles className="w-4 h-4" />
            </span>
          </div>

          <div className="space-y-3">
            {(data?.recommendations || []).map((rec: string, idx: number) => (
              <div key={idx} className="p-3.5 rounded-xl bg-violet-50/50 border border-violet-100 flex items-start gap-3 text-xs text-slate-700">
                <span className="w-5 h-5 rounded-full bg-violet-600 text-white font-bold flex items-center justify-center shrink-0 text-[10px]">
                  {idx + 1}
                </span>
                <span>{rec}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Live Backend Agent Decisions Feed */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-base font-bold text-slate-900">Recent Agent Decisions</h2>
              <p className="text-xs text-slate-500">Observable events persisted in Neon PostgreSQL</p>
            </div>
            <Link to="/agent-center" className="text-xs font-semibold text-violet-600 hover:text-violet-700 flex items-center gap-1">
              Activity Center <ArrowUpRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="space-y-2.5 max-h-64 overflow-y-auto pr-1">
            {(data?.recent_agent_decisions || []).slice(0, 5).map((ev: any) => (
              <div key={ev.id} className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between text-xs">
                <div>
                  <div className="font-semibold text-slate-800 flex items-center gap-1.5">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span className="capitalize">{ev.agent_name.replace("_", " ")}</span>
                  </div>
                  <div className="text-slate-500 text-[11px] truncate max-w-xs">{ev.task}</div>
                </div>
                <div className="text-right">
                  <span className="text-[10px] px-2 py-0.5 rounded font-mono bg-slate-200 text-slate-700">
                    {ev.status}
                  </span>
                  <div className="text-[10px] text-slate-400 mt-1">{ev.duration_ms}ms</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
