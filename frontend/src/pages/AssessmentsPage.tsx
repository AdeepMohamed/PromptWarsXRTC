import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ClipboardCheck, Clock, Award, ArrowRight, BrainCircuit, CheckCircle2, AlertTriangle } from "lucide-react";
import api from "../lib/api";

export function AssessmentsPage() {
  const [assessments, setAssessments] = useState<any[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [aRes, rRes] = await Promise.all([
          api.get("/assessments"),
          api.get("/assessments/results"),
        ]);
        setAssessments(aRes.data.assessments || []);
        setResults(rRes.data.results || []);
      } catch (err) {
        console.error("Failed to load assessments:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Loading Diagnostic Assessments...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
          <ClipboardCheck className="w-3.5 h-3.5" />
          <span>Diagnostic Competency Verification</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900">Assessment Center</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Take targeted skill diagnostics. Scores directly feed Performance Agent evaluation and dynamically adapt your curriculum.
        </p>
      </div>

      {/* Available Diagnostics Grid */}
      <div>
        <h2 className="text-base font-bold text-slate-900 mb-4">Available Skill Diagnostics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assessments.map((a) => (
            <div
              key={a.id}
              className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between hover:border-slate-300 transition"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-violet-100 text-violet-700">
                    {a.skill || "Technical"}
                  </span>
                  <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {a.difficulty || "Intermediate"}
                  </span>
                </div>

                <h3 className="text-base font-bold text-slate-900 mb-2">{a.title}</h3>
                <p className="text-xs text-slate-500 mb-4 line-clamp-2">
                  Rigorous multi-choice and architectural scenario evaluation.
                </p>

                <div className="flex items-center gap-4 text-xs text-slate-500 mb-6">
                  <span className="flex items-center gap-1">
                    <Clock className="w-3.5 h-3.5 text-slate-400" /> {a.time_limit || 25} Mins
                  </span>
                  <span className="flex items-center gap-1">
                    <Award className="w-3.5 h-3.5 text-slate-400" /> {a.question_count || 8} Questions
                  </span>
                </div>
              </div>

              <Link
                to={`/assessments/${a.id}`}
                className="w-full py-2.5 rounded-xl bg-violet-600 hover:bg-violet-500 text-white text-xs font-semibold shadow-md shadow-violet-600/20 transition flex items-center justify-center gap-2"
              >
                Launch Diagnostic <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ))}
        </div>
      </div>

      {/* Past Submissions History */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
        <h2 className="text-base font-bold text-slate-900 mb-1">Assessment Performance History</h2>
        <p className="text-xs text-slate-500 mb-4">Past results evaluated by Performance Agent</p>

        {results.length === 0 ? (
          <div className="text-center py-8 text-xs text-slate-400">
            No assessments completed yet. Launch a diagnostic test above to test your knowledge!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider">
                  <th className="pb-3">Assessment ID</th>
                  <th className="pb-3">Score</th>
                  <th className="pb-3">Percentage</th>
                  <th className="pb-3">Weak Topics Identified</th>
                  <th className="pb-3 text-right">Completion Date</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {results.map((r: any) => {
                  const pct = Number(r.percentage || 0);
                  const isPoor = pct < 50;

                  return (
                    <tr key={r.id} className="hover:bg-slate-50/60 transition">
                      <td className="py-3 font-mono text-slate-600">{r.id.substring(0, 8)}...</td>
                      <td className="py-3 font-semibold text-slate-800">
                        {r.score} / {r.max_score}
                      </td>
                      <td className="py-3 font-bold">
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] ${
                            isPoor
                              ? "bg-red-100 text-red-700"
                              : pct >= 80
                              ? "bg-emerald-100 text-emerald-700"
                              : "bg-amber-100 text-amber-700"
                          }`}
                        >
                          {pct.toFixed(1)}% {isPoor ? "(Remedial Triggered)" : ""}
                        </span>
                      </td>
                      <td className="py-3">
                        <div className="flex flex-wrap gap-1 max-w-xs">
                          {(r.weak_topics || []).slice(0, 3).map((wt: string) => (
                            <span key={wt} className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600">
                              {wt}
                            </span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3 text-right text-slate-400">
                        {new Date(r.completed_at).toLocaleDateString()}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

