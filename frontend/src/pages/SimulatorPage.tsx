import React, { useEffect, useState } from "react";
import { Shuffle, ArrowRight, CheckCircle2, AlertTriangle, Clock, Sparkles, BrainCircuit } from "lucide-react";
import api from "../lib/api";

export function SimulatorPage() {
  const [allCareers, setAllCareers] = useState<any[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [simulations, setSimulations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulating, setSimulating] = useState(false);

  useEffect(() => {
    async function loadCareers() {
      try {
        const res = await api.get("/careers");
        const list = res.data.careers || [];
        setAllCareers(list);

        // Select top 3 careers by default (Full Stack, Data Scientist, AI Engineer)
        const defaults = list.slice(0, 3).map((c: any) => c.id);
        setSelectedIds(defaults);

        if (defaults.length > 0) {
          const simRes = await api.post("/career/simulate", { career_ids: defaults });
          setSimulations(simRes.data.simulations || []);
        }
      } catch (err) {
        console.error("Failed to load simulator data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadCareers();
  }, []);

  const handleToggleCareer = (id: string) => {
    setSelectedIds((prev) => {
      if (prev.includes(id)) {
        if (prev.length <= 1) return prev; // Keep at least 1
        return prev.filter((x) => x !== id);
      } else {
        if (prev.length >= 4) return prev; // Limit to 4 max side-by-side
        return [...prev, id];
      }
    });
  };

  const runSimulation = async () => {
    setSimulating(true);
    try {
      const res = await api.post("/career/simulate", { career_ids: selectedIds });
      setSimulations(res.data.simulations || []);
    } catch (err) {
      console.error("Simulation failed:", err);
    } finally {
      setSimulating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Simulating Transferable Competencies...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
          <Shuffle className="w-3.5 h-3.5" />
          <span>Cross-Role Transferability Matrix</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900">Career What-If Simulator</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Evaluate how your current technical profile maps across multiple alternative paths and discover transferable competencies.
        </p>
      </div>

      {/* Career Selector Pills */}
      <div className="p-5 rounded-2xl bg-white border border-slate-200 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-3">
          <div>
            <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Select 2 to 4 Careers to Compare
            </h2>
            <p className="text-[11px] text-slate-500">Click to toggle active simulator lanes</p>
          </div>

          <button
            onClick={runSimulation}
            disabled={simulating}
            className="px-4 py-2 rounded-xl text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white shadow-md shadow-violet-600/20 transition flex items-center gap-1.5 self-start sm:self-auto"
          >
            <Sparkles className="w-3.5 h-3.5" />
            {simulating ? "Simulating..." : "Recalculate Lanes"}
          </button>
        </div>

        <div className="flex flex-wrap gap-2">
          {allCareers.map((c) => {
            const isSelected = selectedIds.includes(c.id);
            return (
              <button
                key={c.id}
                onClick={() => handleToggleCareer(c.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                  isSelected
                    ? "bg-violet-900 text-white shadow-sm"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {c.title}
              </button>
            );
          })}
        </div>
      </div>

      {/* Side-by-Side Comparison Columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {simulations.map((sim: any) => {
          const readiness = Number(sim.readiness || 0);

          return (
            <div
              key={sim.career?.id || sim.career?.title}
              className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h3 className="text-lg font-bold text-slate-900">{sim.career?.title}</h3>
                  <span className="text-[10px] font-semibold uppercase px-2 py-0.5 rounded bg-slate-100 text-slate-600">
                    {sim.career?.demand_level || "High"}
                  </span>
                </div>

                {/* Readiness Gauge */}
                <div className="my-5 p-4 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-semibold text-slate-600">Estimated Readiness</span>
                    <span className="font-black text-slate-900 text-base">{readiness.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-200 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-violet-600 h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(readiness, 100)}%` }}
                    ></div>
                  </div>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-2 text-xs mb-5">
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                    <div className="text-slate-400 text-[10px] uppercase font-bold">Est. Learning Effort</div>
                    <div className="text-sm font-bold text-slate-800 mt-1 flex items-center gap-1">
                      <Clock className="w-3.5 h-3.5 text-violet-500" /> {sim.effort_hours || 120} hrs
                    </div>
                  </div>
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-100">
                    <div className="text-slate-400 text-[10px] uppercase font-bold">Missing Skills</div>
                    <div className="text-sm font-bold text-amber-700 mt-1">
                      {sim.missing_skills?.length || 0} gaps
                    </div>
                  </div>
                </div>

                {/* Transferable Skills */}
                <div className="mb-4">
                  <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-700 flex items-center gap-1 mb-2">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Transferable Competencies ({sim.transferable_skills?.length || 0})
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {(sim.transferable_skills || []).length === 0 ? (
                      <span className="text-xs text-slate-400 italic">None currently satisfying threshold</span>
                    ) : (
                      (sim.transferable_skills || []).map((sk: string) => (
                        <span key={sk} className="text-[11px] px-2 py-0.5 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
                          {sk}
                        </span>
                      ))
                    )}
                  </div>
                </div>

                {/* Missing Skills */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                    Required Gap Skills ({sim.missing_skills?.length || 0})
                  </h4>
                  <div className="flex flex-wrap gap-1.5">
                    {(sim.missing_skills || []).slice(0, 5).map((sk: string) => (
                      <span key={sk} className="text-[11px] px-2 py-0.5 rounded bg-slate-100 text-slate-700">
                        {sk}
                      </span>
                    ))}
                    {(sim.missing_skills?.length || 0) > 5 && (
                      <span className="text-[10px] text-slate-400 self-center">
                        +{sim.missing_skills.length - 5} more
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
