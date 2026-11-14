import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Sparkles, ArrowRight, CheckCircle2, Sliders, Compass, BrainCircuit, Loader2 } from "lucide-react";
import api from "../lib/api";

export function OnboardingPage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [educationLevel, setEducationLevel] = useState("Bachelor's Degree in Computer Science");
  const [yearsExperience, setYearsExperience] = useState(1);
  const [bio, setBio] = useState("Software developer focused on backend systems, looking to master modern full stack web engineering.");

  const [availableSkills, setAvailableSkills] = useState<any[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<{ [skillId: string]: number }>({});
  const [careers, setCareers] = useState<any[]>([]);
  const [selectedCareerId, setSelectedCareerId] = useState<string>("");

  const [orchestrating, setOrchestrating] = useState(false);
  const [agentStep, setAgentStep] = useState("Initializing Multi-Agent Pipeline...");

  useEffect(() => {
    async function loadData() {
      try {
        const [skillsRes, careersRes] = await Promise.all([
          api.get("/skills"),
          api.get("/careers"),
        ]);
        setAvailableSkills(skillsRes.data.skills || []);
        const carList = careersRes.data.careers || [];
        setCareers(carList);
        if (carList.length > 0) {
          setSelectedCareerId(carList[0].id);
        }

        // Set default starter skills (like Alex Morgan)
        const initSkills: { [id: string]: number } = {};
        for (const s of skillsRes.data.skills || []) {
          if (s.name === "Python") initSkills[s.id] = 80;
          if (s.name === "SQL") initSkills[s.id] = 75;
          if (s.name === "HTML") initSkills[s.id] = 40;
          if (s.name === "CSS") initSkills[s.id] = 20;
          if (s.name === "Git") initSkills[s.id] = 30;
        }
        setSelectedSkills(initSkills);
      } catch (err) {
        console.error("Failed to load onboarding options:", err);
      }
    }
    loadData();
  }, []);

  const handleSkillToggle = (skillId: string) => {
    setSelectedSkills((prev) => {
      const next = { ...prev };
      if (next[skillId] !== undefined) {
        delete next[skillId];
      } else {
        next[skillId] = 50;
      }
      return next;
    });
  };

  const handleProficiencyChange = (skillId: string, val: number) => {
    setSelectedSkills((prev) => ({ ...prev, [skillId]: val }));
  };

  const handleSubmit = async () => {
    setOrchestrating(true);
    setAgentStep("Skill Agent: Analyzing declared competencies...");

    try {
      // 1. Save profile
      await api.put("/learner/profile", {
        education_level: educationLevel,
        years_experience: yearsExperience,
        bio: bio,
        academic_background: "Computer Science & Engineering",
        certifications: ["Intro to Algorithms"],
      });

      // 2. Save skills
      setAgentStep("Career Agent: Evaluating market requirements against Neon DB...");
      const skillPayload = Object.entries(selectedSkills).map(([skill_id, proficiency]) => ({
        skill_id,
        proficiency,
      }));
      if (skillPayload.length > 0) {
        await api.post("/learner/skills", { skills: skillPayload });
      }

      // 3. Set career goal & orchestrate
      setAgentStep("Learning Agent: Generating personalized 6-week curriculum...");
      await api.post("/agents/orchestrate", {
        workflow: "initial_analysis",
        params: { career_id: selectedCareerId },
      });

      setAgentStep("Mentor Agent: Preparing diagnostic career overview...");
      setTimeout(() => {
        navigate("/dashboard");
      }, 1000);
    } catch (err) {
      console.error("Onboarding failed:", err);
      setOrchestrating(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col justify-center py-12 px-6">
      <div className="max-w-2xl mx-auto w-full">
        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            <span>Step {step} of 3</span>
            <span>{step === 1 ? "Background" : step === 2 ? "Skills" : "Target Career"}</span>
          </div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div
              className="bg-gradient-to-r from-violet-600 to-indigo-600 h-full transition-all duration-300"
              style={{ width: `${(step / 3) * 100}%` }}
            ></div>
          </div>
        </div>

        <div className="bg-slate-950 p-8 rounded-3xl border border-slate-800 shadow-2xl relative">
          {orchestrating ? (
            <div className="py-16 text-center">
              <div className="w-16 h-16 rounded-2xl bg-violet-600/20 border border-violet-500/30 text-violet-400 flex items-center justify-center mx-auto mb-6 animate-pulse">
                <BrainCircuit className="w-8 h-8 animate-spin" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">Multi-Agent Orchestration Active</h3>
              <p className="text-sm text-violet-300 font-mono mb-4">{agentStep}</p>
              <div className="text-xs text-slate-500">
                Please wait while Skill Agent, Career Agent, and Learning Agent analyze your profile.
              </div>
            </div>
          ) : (
            <>
              {step === 1 && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-1">Academic & Career Background</h2>
                  <p className="text-sm text-slate-400 mb-6">
                    Our AI agents use your background to contextualize your learning pace.
                  </p>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                        Education Level
                      </label>
                      <input
                        type="text"
                        value={educationLevel}
                        onChange={(e) => setEducationLevel(e.target.value)}
                        className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                        Years of Technical Experience: {yearsExperience}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="10"
                        value={yearsExperience}
                        onChange={(e) => setYearsExperience(Number(e.target.value))}
                        className="w-full accent-violet-500"
                      />
                    </div>

                    <div>
                      <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                        Professional Summary & Goals
                      </label>
                      <textarea
                        rows={3}
                        value={bio}
                        onChange={(e) => setBio(e.target.value)}
                        className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                      />
                    </div>
                  </div>

                  <div className="mt-8 flex justify-end">
                    <button
                      onClick={() => setStep(2)}
                      className="px-6 py-2.5 rounded-xl font-semibold bg-violet-600 hover:bg-violet-500 text-white text-sm flex items-center gap-2"
                    >
                      Continue to Skills <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}

              {step === 2 && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-1">Select Claimed Capabilities</h2>
                  <p className="text-sm text-slate-400 mb-6">
                    Select the technologies you have experience with and set your self-estimated proficiency.
                  </p>

                  <div className="max-h-72 overflow-y-auto space-y-3 pr-2 mb-6">
                    {availableSkills.map((sk) => {
                      const isSelected = selectedSkills[sk.id] !== undefined;
                      const prof = selectedSkills[sk.id] || 0;
                      return (
                        <div
                          key={sk.id}
                          className={`p-3.5 rounded-xl border transition ${
                            isSelected
                              ? "bg-violet-950/30 border-violet-600/50"
                              : "bg-slate-900/60 border-slate-800/80 hover:border-slate-700"
                          }`}
                        >
                          <div className="flex items-center justify-between">
                            <button
                              type="button"
                              onClick={() => handleSkillToggle(sk.id)}
                              className="flex items-center gap-2.5 text-sm font-medium text-white"
                            >
                              <div
                                className={`w-4 h-4 rounded border flex items-center justify-center ${
                                  isSelected ? "bg-violet-600 border-violet-500" : "border-slate-600"
                                }`}
                              >
                                {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-white" />}
                              </div>
                              <span>{sk.name}</span>
                            </button>
                            <span className="text-xs text-slate-400">{prof}%</span>
                          </div>

                          {isSelected && (
                            <div className="mt-3 pt-3 border-t border-violet-900/40">
                              <input
                                type="range"
                                min="0"
                                max="100"
                                value={prof}
                                onChange={(e) => handleProficiencyChange(sk.id, Number(e.target.value))}
                                className="w-full accent-violet-500"
                              />
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>

                  <div className="flex justify-between items-center">
                    <button
                      onClick={() => setStep(1)}
                      className="px-5 py-2.5 rounded-xl text-slate-400 hover:text-white text-sm"
                    >
                      Back
                    </button>
                    <button
                      onClick={() => setStep(3)}
                      className="px-6 py-2.5 rounded-xl font-semibold bg-violet-600 hover:bg-violet-500 text-white text-sm flex items-center gap-2"
                    >
                      Continue to Target Career <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}

              {step === 3 && (
                <div>
                  <h2 className="text-2xl font-bold text-white mb-1">Select Target Career Goal</h2>
                  <p className="text-sm text-slate-400 mb-6">
                    Our Career Agent will pull required competencies from Neon PostgreSQL to calculate your readiness.
                  </p>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-h-72 overflow-y-auto pr-2 mb-6">
                    {careers.map((c) => {
                      const isSelected = selectedCareerId === c.id;
                      return (
                        <button
                          key={c.id}
                          type="button"
                          onClick={() => setSelectedCareerId(c.id)}
                          className={`p-4 rounded-xl border text-left transition ${
                            isSelected
                              ? "bg-violet-950/40 border-violet-500 ring-2 ring-violet-500/20"
                              : "bg-slate-900/70 border-slate-800 hover:border-slate-700"
                          }`}
                        >
                          <div className="flex items-center justify-between mb-1">
                            <span className="font-semibold text-sm text-white">{c.title}</span>
                            <span className="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 uppercase font-medium">
                              {c.demand_level}
                            </span>
                          </div>
                          <p className="text-xs text-slate-400 line-clamp-2">{c.description}</p>
                        </button>
                      );
                    })}
                  </div>

                  <div className="flex justify-between items-center">
                    <button
                      onClick={() => setStep(2)}
                      className="px-5 py-2.5 rounded-xl text-slate-400 hover:text-white text-sm"
                    >
                      Back
                    </button>
                    <button
                      onClick={handleSubmit}
                      className="px-7 py-3 rounded-xl font-semibold bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-lg shadow-violet-600/30 text-sm flex items-center gap-2"
                    >
                      <Sparkles className="w-4 h-4" /> Run Multi-Agent Audit
                    </button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}

