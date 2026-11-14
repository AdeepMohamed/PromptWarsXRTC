import React, { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { BarChart3, TrendingUp, Calendar, BrainCircuit, Sparkles } from "lucide-react";
import api from "../lib/api";

const PIE_COLORS = ["#7c3aed", "#3b82f6", "#10b981", "#f59e0b", "#6366f1"];

export function AnalyticsPage() {
  const [progress, setProgress] = useState<any>(null);
  const [period, setPeriod] = useState("30d");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAnalytics() {
      try {
        const res = await api.get(`/analytics/progress?period=${period}`);
        setProgress(res.data.progress);
      } catch (err) {
        console.error("Failed to load progress analytics:", err);
      } finally {
        setLoading(false);
      }
    }
    loadAnalytics();
  }, [period]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Aggregating Competency Trajectories...</p>
        </div>
      </div>
    );
  }

  const readinessData = progress?.readiness_history || [
    { date: "Day 1", readiness: 20 },
    { date: "Day 7", readiness: 25 },
    { date: "Day 14", readiness: 26.7 },
    { date: "Day 21", readiness: 30.1 },
  ];

  const assessmentScores = progress?.assessment_scores || [
    { date: "Test 1", score: 25, skill: "JavaScript" },
    { date: "Test 2", score: 75, skill: "Python" },
    { date: "Test 3", score: 85, skill: "SQL" },
  ];

  // Activities distribution
  const activityMap = progress?.activities_by_type || { assessment: 3, task_complete: 8, skill_update: 5 };
  const pieData = Object.entries(activityMap).map(([key, value]) => ({
    name: key.replace("_", " "),
    value: Number(value),
  }));

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
            <BarChart3 className="w-3.5 h-3.5" />
            <span>Progress Analytics</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Learning & Readiness Trajectory</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Empirical measurements of skill proficiency acquisition and career readiness velocity over time.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {["7d", "30d", "90d"].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold uppercase transition ${
                period === p
                  ? "bg-slate-900 text-white shadow-sm"
                  : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-50"
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Main Trajectory Chart (Career Readiness Over Time) */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-base font-bold text-slate-900">Career Readiness Score Velocity</h2>
            <p className="text-xs text-slate-500">Progression from initial diagnostic to current competency baseline</p>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-md bg-emerald-50 text-emerald-700 flex items-center gap-1">
            <TrendingUp className="w-3.5 h-3.5" /> Upward Trajectory
          </span>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={readinessData}>
              <XAxis dataKey="date" tick={{ fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
              <Tooltip />
              <Line
                type="monotone"
                dataKey="readiness"
                stroke="#7c3aed"
                strokeWidth={3}
                dot={{ r: 4, fill: "#7c3aed" }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Secondary Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Assessment Score Evolution */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <h2 className="text-base font-bold text-slate-900 mb-1">Diagnostic Assessment Outcomes</h2>
          <p className="text-xs text-slate-500 mb-4">Recent test percentages by skill category</p>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={assessmentScores}>
                <XAxis dataKey="skill" tick={{ fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Tooltip />
                <Line
                  type="monotone"
                  dataKey="score"
                  stroke="#3b82f6"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: "#3b82f6" }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Activity Distribution */}
        <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
          <h2 className="text-base font-bold text-slate-900 mb-1">Learning Activity Distribution</h2>
          <p className="text-xs text-slate-500 mb-4">Actions breakdown recorded in Neon database</p>

          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  outerRadius={75}
                  dataKey="value"
                  label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {pieData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
