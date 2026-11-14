import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Compass, CheckCircle2, ArrowRight, DollarSign, TrendingUp, Sparkles, Plus, BrainCircuit } from "lucide-react";
import api from "../lib/api";

export function CareersPage() {
  const navigate = useNavigate();
  const [careers, setCareers] = useState<any[]>([]);
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [switchingId, setSwitchingId] = useState<string | null>(null);

  const fetchCareers = async () => {
    try {
      const [cRes, pRes] = await Promise.all([
        api.get("/careers"),
        api.get("/learner/profile"),
      ]);
      setCareers(cRes.data.careers || []);
      setProfile(pRes.data.profile);
    } catch (err) {
      console.error("Failed to load careers:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCareers();
  }, []);

  const handleSetGoal = async (careerId: string) => {
    setSwitchingId(careerId);
    try {
      await api.put("/career/goal", { career_id: careerId });
      await fetchCareers();
      navigate("/dashboard");
    } catch (err) {
      console.error("Failed to update career goal:", err);
    } finally {
      setSwitchingId(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Loading Market Career Roles...</p>
        </div>
      </div>
    );
  }

  const activeGoalId = profile?.target_career_id;

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
            <Compass className="w-3.5 h-3.5" />
            <span>Market Demand & Competency Standards</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Career Explorer</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Compare modern technical disciplines and activate automated multi-agent roadmap synthesis.
          </p>
        </div>
      </div>

      {/* Career Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {careers.map((career) => {
          const isCurrentGoal = activeGoalId === career.id;
          const isSwitching = switchingId === career.id;

          return (
            <div
              key={career.id}
              className={`p-6 rounded-2xl bg-white border transition flex flex-col justify-between ${
                isCurrentGoal
                  ? "border-violet-500 ring-2 ring-violet-500/20 shadow-lg shadow-violet-500/5"
                  : "border-slate-200 hover:border-slate-300 shadow-sm"
              }`}
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {career.category || "Technology"}
                  </span>
                  <span className="text-[10px] font-semibold px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 uppercase flex items-center gap-1">
                    <TrendingUp className="w-3 h-3" /> {career.demand_level || "High"} Demand
                  </span>
                </div>

                <h3 className="text-lg font-bold text-slate-900 mb-2">{career.title}</h3>
                <p className="text-xs text-slate-600 leading-relaxed mb-4 line-clamp-3">
                  {career.description}
                </p>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 mb-6 flex items-center justify-between text-xs">
                  <span className="text-slate-500 flex items-center gap-1">
                    <DollarSign className="w-3.5 h-3.5 text-slate-400" /> Avg Compensation
                  </span>
                  <span className="font-semibold text-slate-800">{career.avg_salary_range || "$95,000 - $145,000"}</span>
                </div>
              </div>

              <div>
                {isCurrentGoal ? (
                  <div className="w-full py-2.5 rounded-xl bg-violet-50 border border-violet-200 text-violet-700 text-xs font-semibold flex items-center justify-center gap-2">
                    <CheckCircle2 className="w-4 h-4" /> Active Target Career
                  </div>
                ) : (
                  <button
                    onClick={() => handleSetGoal(career.id)}
                    disabled={isSwitching}
                    className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-violet-600 text-white text-xs font-semibold transition flex items-center justify-center gap-2 disabled:opacity-50"
                  >
                    {isSwitching ? (
                      "Switching & Synthesizing..."
                    ) : (
                      <>
                        Set as Career Goal <ArrowRight className="w-3.5 h-3.5" />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

