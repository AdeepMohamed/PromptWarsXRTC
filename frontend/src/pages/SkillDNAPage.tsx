import React, { useEffect, useState } from "react";
import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";
import { Dna, Plus, Sparkles, CheckCircle2, ShieldCheck, BrainCircuit } from "lucide-react";
import api from "../lib/api";

export function SkillDNAPage() {
  const [profile, setProfile] = useState<any>(null);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [allSkills, setAllSkills] = useState<any[]>([]);

  // Add skill modal
  const [showModal, setShowModal] = useState(false);
  const [selectedSkillId, setSelectedSkillId] = useState("");
  const [newProficiency, setNewProficiency] = useState(50);

  const fetchData = async () => {
    try {
      const [profRes, anaRes, skillsRes] = await Promise.all([
        api.get("/learner/profile"),
        api.post("/skills/analyze"),
        api.get("/skills"),
      ]);
      setProfile(profRes.data.profile);
      setAnalysis(anaRes.data.skill_analysis);
      setAllSkills(skillsRes.data.skills || []);
      if (skillsRes.data.skills?.length > 0) {
        setSelectedSkillId(skillsRes.data.skills[0].id);
      }
    } catch (err) {
      console.error("Failed to load skill DNA:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddSkill = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.post("/learner/skills", {
        skills: [{ skill_id: selectedSkillId, proficiency: newProficiency }],
      });
      setShowModal(false);
      await fetchData();
    } catch (err) {
      console.error("Failed to add skill:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Generating Skill DNA Radar...</p>
        </div>
      </div>
    );
  }

  const rawDna = analysis?.skill_dna || {};
  const radarData = [
    { subject: "Programming", value: Math.round(rawDna.programming || 35), fullMark: 100 },
    { subject: "Analytical Thinking", value: Math.round(rawDna.analytical_thinking || 40), fullMark: 100 },
    { subject: "Problem Solving", value: Math.round(rawDna.problem_solving || 45), fullMark: 100 },
    { subject: "Communication", value: Math.round(rawDna.communication || 30), fullMark: 100 },
    { subject: "Technical Proficiency", value: Math.round(rawDna.technical_proficiency || 50), fullMark: 100 },
    { subject: "Project Experience", value: Math.round(rawDna.project_experience || 20), fullMark: 100 },
  ];

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
            <Dna className="w-3.5 h-3.5" />
            <span>Multi-Dimensional Competency Fingerprint</span>
          </div>
          <h1 className="text-2xl font-bold text-slate-900">My Skill DNA</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Holistic capability profile synthesizing claimed knowledge, assessment tests, and project history.
          </p>
        </div>

        <button
          onClick={() => setShowModal(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white shadow-md shadow-violet-600/20 transition self-start sm:self-auto"
        >
          <Plus className="w-4 h-4" /> Add Skill Entry
        </button>
      </div>

      {/* Main Grid: Radar Visualization + Dimension Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Radar Chart Card (7 Cols) */}
        <div className="lg:col-span-7 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col items-center justify-center">
          <div className="w-full flex items-center justify-between mb-2">
            <h2 className="text-base font-bold text-slate-900">Skill DNA Radar</h2>
            <span className="text-xs text-slate-400 font-mono">6 Dimensions</span>
          </div>
          <div className="w-full h-80">
            <ResponsiveContainer width="100%" height="100%">
              <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                <PolarGrid stroke="#e2e8f0" />
                <PolarAngleAxis dataKey="subject" tick={{ fill: "#475569", fontSize: 11, fontWeight: 500 }} />
                <PolarRadiusAxis angle={30} domain={[0, 100]} stroke="#cbd5e1" />
                <Radar
                  name="Proficiency"
                  dataKey="value"
                  stroke="#7c3aed"
                  fill="#7c3aed"
                  fillOpacity={0.4}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Dimension Breakdown Card (5 Cols) */}
        <div className="lg:col-span-5 p-6 rounded-2xl bg-white border border-slate-200 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 mb-1">Fingerprint Diagnostics</h2>
            <p className="text-xs text-slate-500 mb-4">Calculated by COGNIFY Skill Agent</p>

            <div className="space-y-3">
              {radarData.map((d) => (
                <div key={d.subject} className="p-2.5 rounded-xl bg-slate-50 border border-slate-100 flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-700">{d.subject}</span>
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-slate-200 h-2 rounded-full overflow-hidden">
                      <div className="bg-violet-600 h-full rounded-full" style={{ width: `${d.value}%` }}></div>
                    </div>
                    <span className="text-xs font-bold text-slate-900 w-8 text-right">{d.value}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs text-slate-500">
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
            <span>Assessed scores automatically recalibrate radar dimensions.</span>
          </div>
        </div>
      </div>

      {/* Verified Skills Inventory Table */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h2 className="text-base font-bold text-slate-900">Declared & Assessed Skill Inventory</h2>
            <p className="text-xs text-slate-500">Every competence is tracked with provenance and confidence tier</p>
          </div>
          <span className="text-xs px-2.5 py-1 rounded-full bg-slate-100 text-slate-700 font-semibold">
            {profile?.skills?.length || 0} Registered Skills
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-100 text-slate-400 font-semibold uppercase tracking-wider">
                <th className="pb-3">Skill Name</th>
                <th className="pb-3">Proficiency</th>
                <th className="pb-3">Confidence Tier</th>
                <th className="pb-3">Evidence Source</th>
                <th className="pb-3 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {(profile?.skills || []).map((sk: any) => (
                <tr key={sk.skill_id} className="hover:bg-slate-50/60 transition">
                  <td className="py-3.5 font-bold text-slate-800">{sk.name}</td>
                  <td className="py-3.5">
                    <div className="flex items-center gap-2">
                      <div className="w-28 bg-slate-100 h-2 rounded-full overflow-hidden">
                        <div
                          className="bg-violet-600 h-full rounded-full"
                          style={{ width: `${sk.proficiency}%` }}
                        ></div>
                      </div>
                      <span className="font-semibold text-slate-700">{sk.proficiency}%</span>
                    </div>
                  </td>
                  <td className="py-3.5">
                    <span
                      className={`px-2 py-0.5 rounded-full font-medium capitalize text-[10px] ${
                        sk.confidence === "assessed"
                          ? "bg-emerald-100 text-emerald-800"
                          : sk.confidence === "demonstrated"
                          ? "bg-blue-100 text-blue-800"
                          : "bg-slate-100 text-slate-600"
                      }`}
                    >
                      {sk.confidence}
                    </span>
                  </td>
                  <td className="py-3.5 text-slate-500 capitalize">{sk.source.replace("_", " ")}</td>
                  <td className="py-3.5 text-right font-medium">
                    {sk.proficiency >= 70 ? (
                      <span className="text-emerald-600">Mastered</span>
                    ) : sk.proficiency >= 40 ? (
                      <span className="text-indigo-600">Developing</span>
                    ) : (
                      <span className="text-amber-600">Foundational</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Modal to Add Skill */}
      {showModal && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-200">
            <h3 className="text-lg font-bold text-slate-900 mb-1">Add Skill Competency</h3>
            <p className="text-xs text-slate-500 mb-4">Declare a new skill or self-report starting proficiency.</p>

            <form onSubmit={handleAddSkill} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                  Select Technology / Skill
                </label>
                <select
                  value={selectedSkillId}
                  onChange={(e) => setSelectedSkillId(e.target.value)}
                  className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800"
                >
                  {allSkills.map((s) => (
                    <option key={s.id} value={s.id}>
                      {s.name} ({s.category})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1">
                  Estimated Proficiency: {newProficiency}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={newProficiency}
                  onChange={(e) => setNewProficiency(Number(e.target.value))}
                  className="w-full accent-violet-600"
                />
              </div>

              <div className="flex justify-end gap-2 pt-4 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-xl text-xs text-slate-500 hover:text-slate-700"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl text-xs font-semibold bg-violet-600 hover:bg-violet-500 text-white"
                >
                  Save Entry
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
