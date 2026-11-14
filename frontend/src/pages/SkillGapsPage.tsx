import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Target, AlertCircle, CheckCircle2, AlertTriangle, ArrowRight, BrainCircuit, Sparkles } from "lucide-react";
import api from "../lib/api";

export function SkillGapsPage() {
  const [profile, setProfile] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [gaps, setGaps] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchGaps = async () => {
    try {
      const [profRes, gapsRes] = await Promise.all([
        api.get("/learner/profile"),
        api.get("/skills/gaps"),
      ]);
      setProfile(profRes.data.profile);
      setGaps(gapsRes.data.gaps || []);

      // If career is selected, run career analysis
      if (profRes.data.profile?.target_career_id) {
        const canaRes = await api.post("/career/analyze", {
          career_id: profRes.data.profile.target_career_id,
        });
        setAnalysis(canaRes.data.analysis);
      }
    } catch (err) {
      console.error("Failed to load skill gap data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGaps();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Calculating Weighted Skill Gaps...</p>
        </div>
      </div>
    );
  }

  const readiness = Number(profile?.career_readiness_score || 0);

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
            <Target className="w-3.5 h-3.5" />
            <span>Career Readiness Intelligence</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">Skill Gap Analysis</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Target Role: <strong className="text-slate-800">{profile?.target_career?.title || "Full Stack Developer"}</strong>
          </p>
        </div>

        <Link
          to="/roadmap"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white shadow-md shadow-violet-600/20 transition self-start sm:self-auto"
        >
          View Remedial Roadmap <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* Readiness Hero & Formula Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Score Card */}
        <div className="p-6 rounded-2xl bg-gradient-to-br from-violet-900 via-indigo-950 to-slate-950 text-white shadow-xl flex flex-col justify-between">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-violet-300">Estimated Career Readiness</span>
            <div className="text-5xl font-black tracking-tight my-4 text-white">
              {readiness.toFixed(1)}%
            </div>
            <div className="w-full bg-violet-950/60 h-2.5 rounded-full overflow-hidden mb-3 border border-violet-800/40">
              <div
                className="bg-gradient-to-r from-violet-400 to-indigo-300 h-full rounded-full"
                style={{ width: `${Math.min(readiness, 100)}%` }}
              ></div>
            </div>
          </div>
          <p className="text-[11px] text-violet-300/80 leading-relaxed">
            *Notice: Calculated from authenticated learner assessment history and weighted market competencies. Not a guarantee of employment.
          </p>
        </div>

        {/* Formula Explanation Card */}
        <div className="md:col-span-2 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-base font-bold text-slate-900">Weighted Mathematical Formulation</h2>
              <span className="text-xs px-2 py-0.5 rounded bg-violet-50 text-violet-700 font-mono font-semibold">
                Formula v2.0
              </span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed mb-4">
              COGNIFY AI does not use arbitrary approximations. Career Readiness is computed as the normalized dot product of learner proficiency and required skill importance weights:
            </p>
            <div className="p-4 rounded-xl bg-slate-900 text-violet-300 font-mono text-xs overflow-x-auto shadow-inner">
              Career Readiness = ∑(Current Proficiency × Skill Importance) ÷ ∑(Skill Importance)
            </div>
          </div>
          <div className="pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-500">
            <span>Critical Gaps Weight Multiplier: 1.5x</span>
            <span>Target Benchmark: 75.0% for Interview Readiness</span>
          </div>
        </div>
      </div>

      {/* Competency Gap Breakdown Bar Chart Table */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-base font-bold text-slate-900">Required Competency Gap Breakdown</h2>
            <p className="text-xs text-slate-500">Current proficiency vs Minimum requirement for target career</p>
          </div>
          <div className="flex items-center gap-4 text-xs font-medium">
            <span className="flex items-center gap-1.5 text-slate-600">
              <span className="w-3 h-3 rounded-sm bg-violet-600"></span> Current
            </span>
            <span className="flex items-center gap-1.5 text-slate-600">
              <span className="w-3 h-3 rounded-sm bg-slate-200 border border-slate-300"></span> Required
            </span>
          </div>
        </div>

        <div className="space-y-4">
          {gaps.length === 0 ? (
            <div className="text-center py-8 text-xs text-slate-500">
              All competency requirements satisfied or no career selected.
            </div>
          ) : (
            gaps.map((g: any) => {
              const current = Number(g.current_proficiency || 0);
              const required = Number(g.required_proficiency || 70);
              const isMet = current >= required;
              const gapVal = Math.max(0, required - current);
              const isCrit = g.is_critical || gapVal > 50;

              return (
                <div key={g.skill} className="p-4 rounded-xl bg-slate-50 border border-slate-100 transition hover:border-slate-200">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <span className="font-bold text-sm text-slate-900">{g.skill}</span>
                      {isCrit && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-red-100 text-red-700 flex items-center gap-1">
                          <AlertTriangle className="w-3 h-3" /> Critical Gap
                        </span>
                      )}
                      {isMet && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-semibold bg-emerald-100 text-emerald-700 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Meets Requirement
                        </span>
                      )}
                    </div>
                    <div className="text-xs font-mono font-medium text-slate-600">
                      Current: <strong className="text-slate-900">{current}%</strong> / Required: <strong>{required}%</strong>
                    </div>
                  </div>

                  {/* Dual Bar Graphic */}
                  <div className="relative w-full h-4 bg-slate-200 rounded-full overflow-hidden">
                    {/* Required Target Marker */}
                    <div
                      className="absolute top-0 bottom-0 border-r-2 border-slate-800 z-10"
                      style={{ left: `${required}%` }}
                      title={`Target: ${required}%`}
                    ></div>
                    {/* Current Fill */}
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        isMet
                          ? "bg-emerald-500"
                          : isCrit
                          ? "bg-red-500"
                          : "bg-amber-500"
                      }`}
                      style={{ width: `${Math.min(current, 100)}%` }}
                    ></div>
                  </div>

                  <div className="flex justify-between items-center mt-2 text-[11px] text-slate-500">
                    <span>Deficit: {gapVal}% proficiency missing</span>
                    <span>Importance: {g.importance}/10</span>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}
