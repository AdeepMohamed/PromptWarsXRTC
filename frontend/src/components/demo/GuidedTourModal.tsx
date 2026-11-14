import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Sparkles,
  ChevronRight,
  ChevronLeft,
  X,
  Compass,
  CheckCircle2,
  AlertTriangle,
  BrainCircuit,
  Bot,
  Map,
  Target,
  BarChart3,
  Dna,
} from "lucide-react";

export interface TourStep {
  title: string;
  tagline: string;
  path: string;
  agent: string;
  description: string;
  keyMetric: string;
  judgeHighlight: string;
}

const TOUR_STEPS: TourStep[] = [
  {
    title: "Step 1: Career Intelligence Command Center",
    tagline: "Alex's Target Career: Full Stack Developer",
    path: "/dashboard",
    agent: "Central Orchestrator",
    description:
      "Alex Morgan onboarded with Python (85%) & SQL (75%) but 0% React/Node.js experience. The 5-agent orchestrator evaluated role requirements against Neon PostgreSQL benchmarks.",
    keyMetric: "Career Readiness: 42.5% | Progress: Week 4 / 6",
    judgeHighlight:
      "Observe the 4 primary KPI cards, dynamic weekly activity charts, and the live agent decision audit log streamed directly from the database.",
  },
  {
    title: "Step 2: Multi-Dimensional Skill DNA",
    tagline: "Evidence-Backed Competency Fingerprint",
    path: "/skill-dna",
    agent: "Skill Agent",
    description:
      "The Skill Agent continuously calibrates Alex's 6 competency dimensions (Programming, Analytical Thinking, Problem Solving, Communication, Technical Proficiency, Project Experience) backed by multi-tier evidence.",
    keyMetric: "8 Tracked Skills | Technical Proficiency: 43.1%",
    judgeHighlight:
      "The interactive radar chart reflects real assessments and verified project code. Confidence badges (claimed, assessed, demonstrated) show true evidentiary depth.",
  },
  {
    title: "Step 3: Weighted Skill Gap Analysis",
    tagline: "Target Role: Full Stack Developer",
    path: "/skill-gaps",
    agent: "Career Agent",
    description:
      "The Career Agent calculates weighted skill distances to target role benchmarks. JavaScript, React, and Node.js are identified as critical blockers.",
    keyMetric: "Priority Gap #1: React (Target 80%, Current 15%)",
    judgeHighlight:
      "Skills are ranked by gap severity with actionable priority badges and direct transferability mappings from Python/SQL.",
  },
  {
    title: "Step 4: Observable Agent Activity Center",
    tagline: "Multi-Agent Collaboration Audit Trail",
    path: "/agent-center",
    agent: "5 Specialized Agents",
    description:
      "Inspect every independent agent decision in real time: Skill Agent, Career Agent, Learning Agent, Performance Agent, and Mentor Agent. Every event is logged with microsecond execution metrics.",
    keyMetric: "9 Agent Events Logged | Average Latency: 145ms",
    judgeHighlight:
      "Shows genuine multi-agent autonomy. Review inputs, outputs, timestamps, and structured JSON payloads for each agent's decisions.",
  },
  {
    title: "Step 5: Adaptive 6-Week Learning Roadmap",
    tagline: "Weeks 1–3 Completed, Week 4 In-Progress",
    path: "/roadmap",
    agent: "Learning Agent",
    description:
      "The Learning Agent synthesized a 28-task, milestone-driven curriculum tailored to Alex's background. Weeks 1–3 (HTML, CSS, JS) are completed with verified portfolio projects.",
    keyMetric: "14 of 28 Tasks Completed (50.0% Progress)",
    judgeHighlight:
      "Notice how Week 4 dynamically updated following Alex's diagnostic test! Look for the orange [REMEDIAL] tasks injected autonomously.",
  },
  {
    title: "Step 6: Diagnostic Assessment System",
    tagline: "Continuous Proficiency Verification",
    path: "/assessments",
    agent: "Performance Agent",
    description:
      "Alex completed assessments across HTML/CSS (85%), JavaScript (78%), and Advanced JS (88%). But on Week 4, Alex took the React Fundamentals Diagnostic and struggled.",
    keyMetric: "Week 4 Score: 45% (9/20 points) — FAILED",
    judgeHighlight:
      "The platform doesn't just record scores: it passes failure diagnostics to the orchestrator to trigger autonomous curriculum adaptation.",
  },
  {
    title: "Step 7: Autonomous Remedial Intervention",
    tagline: "Performance Agent -> Learning Agent Loop",
    path: "/roadmap",
    agent: "Performance & Learning Agents",
    description:
      "When Alex scored 45% on React Fundamentals, the Performance Agent identified specific concept gaps: useState, useEffect, and Context API. The Learning Agent automatically injected 3 targeted remedial modules into Week 4.",
    keyMetric: "3 Remedial Tasks Injected Autonomously",
    judgeHighlight:
      "Demonstrates real adaptive intelligence: the roadmap actively reformed itself in response to measured learner struggle rather than static pre-canned paths.",
  },
  {
    title: "Step 8: Context-Aware AI Mentor",
    tagline: "Personalized Remediation Coaching",
    path: "/mentor",
    agent: "Mentor Agent",
    description:
      "The AI Mentor maintains full contextual awareness of Alex's recent diagnostic test failure, roadmap adaptations, and project goals, answering questions with targeted technical explanations.",
    keyMetric: "Gemini / Grok LLM Intelligence + Database Memory",
    judgeHighlight:
      "Ask the mentor about React hooks or click any prompt pill to observe personalized, empathetic, technically grounded guidance.",
  },
  {
    title: "Step 9: Project Verification Engine",
    tagline: "Evidence-Based Skill Certification",
    path: "/projects",
    agent: "Skill & Project Verification",
    description:
      "Alex submitted 3 verified GitHub repositories: Personal Portfolio Website (verified), Interactive Calculator (verified), and Task Management Application (pending review).",
    keyMetric: "3 Submitted Projects | 2 Verified Deliverables",
    judgeHighlight:
      "Each project has demonstrated skill extraction, repository links, and AI evaluation notes providing verifiable proof of capability.",
  },
  {
    title: "Step 10: Career Intelligence Analytics",
    tagline: "Measurable Learner Progress & Velocity",
    path: "/analytics",
    agent: "Analytics Engine",
    description:
      "Review the trajectory of Alex's transformation: readiness increased from 24.4% to 42.5%, skill improvement timelines, assessment score histories, and projected readiness milestone dates.",
    keyMetric: "+18.1% Readiness Gain in 4 Weeks",
    judgeHighlight:
      "A complete executive dashboard demonstrating that COGNIFY AI produces verifiable, measurable career growth.",
  },
];

export function GuidedTourModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const navigate = useNavigate();

  if (!isOpen) return null;

  const currentStep = TOUR_STEPS[currentStepIndex];

  const handleNext = () => {
    if (currentStepIndex < TOUR_STEPS.length - 1) {
      const nextIdx = currentStepIndex + 1;
      setCurrentStepIndex(nextIdx);
      navigate(TOUR_STEPS[nextIdx].path);
    } else {
      onClose();
    }
  };

  const handlePrev = () => {
    if (currentStepIndex > 0) {
      const prevIdx = currentStepIndex - 1;
      setCurrentStepIndex(prevIdx);
      navigate(TOUR_STEPS[prevIdx].path);
    }
  };

  const handleGoToStep = (idx: number) => {
    setCurrentStepIndex(idx);
    navigate(TOUR_STEPS[idx].path);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4 bg-slate-950/60 backdrop-blur-sm animate-fade-in">
      <div className="w-full max-w-xl bg-slate-900 border border-violet-500/30 rounded-2xl shadow-2xl shadow-violet-950/50 p-6 text-white relative overflow-hidden">
        {/* Glow Accent */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-violet-600/10 rounded-full blur-3xl pointer-events-none" />

        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <span className="p-1.5 rounded-lg bg-violet-600/30 text-violet-400 border border-violet-500/40">
              <Sparkles className="w-4 h-4" />
            </span>
            <div>
              <h3 className="text-sm font-bold tracking-tight text-white">
                Interactive Journey: Alex Morgan
              </h3>
              <p className="text-[11px] text-slate-400">
                Step {currentStepIndex + 1} of {TOUR_STEPS.length}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Step Content */}
        <div className="py-4 space-y-3">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-violet-500/20 text-violet-300 text-[10px] font-semibold border border-violet-500/30 mb-1.5">
              <BrainCircuit className="w-3 h-3" />
              <span>{currentStep.agent}</span>
            </div>
            <h4 className="text-base font-bold text-slate-100">{currentStep.title}</h4>
            <p className="text-xs text-violet-300 font-medium">{currentStep.tagline}</p>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed">
            {currentStep.description}
          </p>

          {/* Key Metric Pill */}
          <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700/60 flex items-center justify-between">
            <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
              Live Metric
            </span>
            <span className="text-xs font-mono font-bold text-emerald-400">
              {currentStep.keyMetric}
            </span>
          </div>

          {/* Judge Tip */}
          <div className="p-3 rounded-xl bg-violet-950/40 border border-violet-800/40 text-xs text-slate-300">
            <span className="font-semibold text-violet-300">Judges Note: </span>
            {currentStep.judgeHighlight}
          </div>
        </div>

        {/* Step Progress Dots */}
        <div className="flex items-center justify-center gap-1.5 py-2">
          {TOUR_STEPS.map((_, idx) => (
            <button
              key={idx}
              onClick={() => handleGoToStep(idx)}
              className={`h-1.5 rounded-full transition-all ${
                idx === currentStepIndex
                  ? "w-6 bg-violet-500"
                  : "w-2 bg-slate-700 hover:bg-slate-600"
              }`}
            />
          ))}
        </div>

        {/* Footer Controls */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <button
            onClick={handlePrev}
            disabled={currentStepIndex === 0}
            className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition disabled:opacity-40 disabled:hover:bg-transparent flex items-center gap-1"
          >
            <ChevronLeft className="w-3.5 h-3.5" /> Previous
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate(currentStep.path)}
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 border border-slate-700 transition"
            >
              Go to Page
            </button>
            <button
              onClick={handleNext}
              className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-md shadow-violet-600/30 transition flex items-center gap-1"
            >
              {currentStepIndex === TOUR_STEPS.length - 1 ? (
                "Finish Tour"
              ) : (
                <>
                  Next Step <ChevronRight className="w-3.5 h-3.5" />
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
