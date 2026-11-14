import React from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Sparkles,
  ArrowRight,
  BrainCircuit,
  Target,
  Compass,
  Map,
  ClipboardCheck,
  Bot,
  Building2,
  GraduationCap,
  ShieldCheck,
  Zap,
} from "lucide-react";
import { useAuthContext } from "../contexts/AuthContext";

export function LandingPage() {
  const navigate = useNavigate();
  const { login } = useAuthContext();

  const handleDemoLogin = async () => {
    try {
      await login("alex@cognify.ai", "password123");
      navigate("/dashboard");
    } catch {
      navigate("/login");
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col selection:bg-violet-500 selection:text-white">
      {/* Header */}
      <header className="border-b border-slate-800/80 backdrop-blur-md sticky top-0 z-50 bg-slate-900/80">
        <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-violet-500/25">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight text-white flex items-center gap-1.5">
              COGNIFY <span className="text-violet-400 text-xs px-2 py-0.5 rounded bg-violet-950/80 border border-violet-800/60 font-semibold">AI</span>
            </span>
          </div>

          <nav className="hidden md:flex items-center space-x-8 text-sm font-medium text-slate-300">
            <a href="#agents" className="hover:text-white transition">Agent Architecture</a>
            <a href="#how-it-works" className="hover:text-white transition">How It Works</a>
            <a href="#features" className="hover:text-white transition">Career Intelligence</a>
            <a href="#institutions" className="hover:text-white transition">Enterprise & Universities</a>
          </nav>

          <div className="flex items-center space-x-3">
            <button
              onClick={handleDemoLogin}
              className="text-xs px-3.5 py-2 rounded-lg font-medium text-violet-300 border border-violet-700/60 bg-violet-950/40 hover:bg-violet-900/40 transition"
            >
              Demo: Alex Morgan
            </button>
            <Link
              to="/login"
              className="text-sm font-medium text-slate-300 hover:text-white px-3 py-2 transition"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="text-sm font-medium px-4 py-2 rounded-lg bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-md shadow-violet-600/30 transition"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-24 pb-20 px-6 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(124,58,237,0.25),rgba(255,255,255,0))]"></div>
        <div className="max-w-5xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full border border-violet-500/30 bg-violet-950/50 text-violet-300 text-xs font-semibold mb-8 shadow-inner">
            <Zap className="w-3.5 h-3.5 text-violet-400" />
            <span>Agentic AI Career Intelligence & Adaptive Learning</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white mb-6 leading-[1.1]">
            Your Future Deserves a{" "}
            <span className="bg-gradient-to-r from-violet-400 via-indigo-300 to-blue-400 bg-clip-text text-transparent">
              Smarter Learning Path.
            </span>
          </h1>

          <p className="text-lg md:text-xl text-slate-300 max-w-3xl mx-auto mb-10 leading-relaxed">
            Discover your strengths, identify skill gaps and achieve your target career through genuine AI agent collaboration, real-time diagnostic evaluation, and self-adapting learning roadmaps.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-7 py-3.5 rounded-xl font-semibold bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-lg shadow-violet-600/40 transition text-base"
            >
              Analyze My Career Readiness <ArrowRight className="w-4 h-4" />
            </Link>
            <button
              onClick={handleDemoLogin}
              className="w-full sm:w-auto px-7 py-3.5 rounded-xl font-medium bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-slate-200 transition text-base"
            >
              Launch Live Demo Account
            </button>
          </div>

          {/* Quick Metrics Bar */}
          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto border-t border-slate-800 pt-10 text-left">
            <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800">
              <div className="text-2xl font-bold text-white mb-1">5 Specialized</div>
              <div className="text-xs text-slate-400 font-medium">Independent AI Agents</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800">
              <div className="text-2xl font-bold text-violet-400 mb-1">Neon Postgres</div>
              <div className="text-xs text-slate-400 font-medium">Persistent Competency Store</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800">
              <div className="text-2xl font-bold text-emerald-400 mb-1">Adaptive</div>
              <div className="text-xs text-slate-400 font-medium">Real-Time Remediation</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-800">
              <div className="text-2xl font-bold text-indigo-400 mb-1">Zero Gimmicks</div>
              <div className="text-xs text-slate-400 font-medium">Pure Observable Backend Logs</div>
            </div>
          </div>
        </div>
      </section>

      {/* 5-Agent Architecture Section */}
      <section id="agents" className="py-24 bg-slate-950/60 border-t border-slate-800 relative">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-violet-400 mb-3">Multi-Agent AI Architecture</h2>
            <h3 className="text-3xl md:text-4xl font-extrabold text-white mb-4">Five Specialized Collaborating Agents</h3>
            <p className="text-slate-400 text-base">
              COGNIFY AI replaces monolithic chatbots with a distributed committee of five specialized agent modules coordinated by a central orchestrator.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-5">
            {/* Agent 1 */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-violet-500/50 transition relative group">
              <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 text-violet-400 flex items-center justify-center mb-4">
                <BrainCircuit className="w-5 h-5" />
              </div>
              <div className="text-xs font-semibold text-violet-400 uppercase tracking-wider mb-1">Agent 01</div>
              <h4 className="text-lg font-bold text-white mb-2">Skill Agent</h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Audits profile, certifications, and code projects to calculate exact proficiencies and generate your 6-axis Skill DNA radar.
              </p>
              <div className="text-[11px] font-mono text-slate-500 border-t border-slate-800 pt-3">
                Outputs: Technical vs Claimed vs Assessed
              </div>
            </div>

            {/* Agent 2 */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-indigo-500/50 transition relative group">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-4">
                <Compass className="w-5 h-5" />
              </div>
              <div className="text-xs font-semibold text-indigo-400 uppercase tracking-wider mb-1">Agent 02</div>
              <h4 className="text-lg font-bold text-white mb-2">Career Agent</h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Pulls real-world market competency matrices from Neon, computes weighted readiness formulas, and flags critical blocking gaps.
              </p>
              <div className="text-[11px] font-mono text-slate-500 border-t border-slate-800 pt-3">
                Formula: ∑(Prof × Weight) / ∑(Weight)
              </div>
            </div>

            {/* Agent 3 */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-blue-500/50 transition relative group">
              <div className="w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center mb-4">
                <Map className="w-5 h-5" />
              </div>
              <div className="text-xs font-semibold text-blue-400 uppercase tracking-wider mb-1">Agent 03</div>
              <h4 className="text-lg font-bold text-white mb-2">Learning Agent</h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Synthesizes individualized 6-week curriculum roadmaps with prerequisite dependencies, practical code exercises, and milestones.
              </p>
              <div className="text-[11px] font-mono text-slate-500 border-t border-slate-800 pt-3">
                Outputs: Weekly Structured Tasks
              </div>
            </div>

            {/* Agent 4 */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-amber-500/50 transition relative group">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400 flex items-center justify-center mb-4">
                <ClipboardCheck className="w-5 h-5" />
              </div>
              <div className="text-xs font-semibold text-amber-400 uppercase tracking-wider mb-1">Agent 04</div>
              <h4 className="text-lg font-bold text-white mb-2">Performance Agent</h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Evaluates test responses, pinpoints weak concepts, updates skill proficiencies, and triggers automatic remedial interventions.
              </p>
              <div className="text-[11px] font-mono text-slate-500 border-t border-slate-800 pt-3">
                Triggers: Poor Score Remediation
              </div>
            </div>

            {/* Agent 5 */}
            <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-emerald-500/50 transition relative group">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-4">
                <Bot className="w-5 h-5" />
              </div>
              <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-1">Agent 05</div>
              <h4 className="text-lg font-bold text-white mb-2">Mentor Agent</h4>
              <p className="text-xs text-slate-400 leading-relaxed mb-4">
                Answers technical questions and delivers tailored guidance using your live skill history and assessment mistakes.
              </p>
              <div className="text-[11px] font-mono text-slate-500 border-t border-slate-800 pt-3">
                Context: Full Authenticated Learner
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="py-24 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-xs font-bold uppercase tracking-wider text-violet-400 mb-3">Workflow</h2>
            <h3 className="text-3xl md:text-4xl font-extrabold text-white mb-4">From Initial Audit to Career Readiness</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-800">
              <div className="text-3xl font-black text-violet-400 mb-3">01</div>
              <h4 className="text-lg font-bold text-white mb-2">Declare Profile</h4>
              <p className="text-sm text-slate-400">
                Input your background, claimed skills, and target career goal (e.g., Full Stack Developer).
              </p>
            </div>
            <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-800">
              <div className="text-3xl font-black text-indigo-400 mb-3">02</div>
              <h4 className="text-lg font-bold text-white mb-2">Multi-Agent Audit</h4>
              <p className="text-sm text-slate-400">
                Skill Agent & Career Agent cross-reference competencies with Neon PostgreSQL requirements.
              </p>
            </div>
            <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-800">
              <div className="text-3xl font-black text-blue-400 mb-3">03</div>
              <h4 className="text-lg font-bold text-white mb-2">Roadmap & Tests</h4>
              <p className="text-sm text-slate-400">
                Follow your structured 6-week curriculum and take diagnostic skill assessments.
              </p>
            </div>
            <div className="p-6 rounded-2xl bg-slate-800/30 border border-slate-800">
              <div className="text-3xl font-black text-emerald-400 mb-3">04</div>
              <h4 className="text-lg font-bold text-white mb-2">Adaptive Growth</h4>
              <p className="text-sm text-slate-400">
                Performance Agent evaluates mistakes and dynamically alters your roadmap until you reach verified readiness.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Institutional Value */}
      <section id="institutions" className="py-24 bg-slate-950/80 border-t border-slate-800">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <div className="p-8 rounded-3xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-violet-600/10 border border-violet-500/20 text-violet-400 flex items-center justify-center mb-6">
                  <GraduationCap className="w-6 h-6" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">For Universities & Colleges</h3>
                <p className="text-slate-300 text-sm leading-relaxed mb-6">
                  Empower students to understand how coursework maps directly to hiring competencies. Enable academic advisors to pinpoint syllabus gaps against real-time industry demands.
                </p>
                <ul className="space-y-3 text-sm text-slate-400">
                  <li className="flex items-center gap-2.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Automated portfolio and project verification</span>
                  </li>
                  <li className="flex items-center gap-2.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Transparent diagnostic scoring distinguishing claimed vs assessed knowledge</span>
                  </li>
                  <li className="flex items-center gap-2.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Personalized AI mentoring for every enrolled learner</span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="p-8 rounded-3xl bg-slate-900 border border-slate-800 flex flex-col justify-between">
              <div>
                <div className="w-12 h-12 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 text-indigo-400 flex items-center justify-center mb-6">
                  <Building2 className="w-6 h-6" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">For Enterprise & Organizations</h3>
                <p className="text-slate-300 text-sm leading-relaxed mb-6">
                  Scale internal mobility and reskilling programs. Eliminate redundant training costs by pinpointing exactly which technical competencies an employee possesses and what they need for promotion.
                </p>
                <ul className="space-y-3 text-sm text-slate-400">
                  <li className="flex items-center gap-2.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>What-If career simulation to identify internal talent mobility</span>
                  </li>
                  <li className="flex items-center gap-2.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Automated remedial learning intervention triggered upon assessment failure</span>
                  </li>
                  <li className="flex items-center gap-2.5">
                    <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Measurable ROI tracked through Neon competency persistence</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer CTA */}
      <footer className="py-20 border-t border-slate-800 text-center relative overflow-hidden">
        <div className="max-w-4xl mx-auto px-6 relative z-10">
          <h2 className="text-3xl md:text-4xl font-extrabold text-white mb-4">
            Transform Your Knowledge into Career Intelligence Today.
          </h2>
          <p className="text-slate-400 text-base mb-8 max-w-xl mx-auto">
            Experience collaborative multi-agent career reasoning in action.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              to="/register"
              className="px-8 py-3.5 rounded-xl font-semibold bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white shadow-lg shadow-violet-600/30 transition"
            >
              Start Free As Learner
            </Link>
            <button
              onClick={handleDemoLogin}
              className="px-8 py-3.5 rounded-xl font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
            >
              Explore Alex Morgan Demo
            </button>
          </div>
          <p className="text-xs text-slate-400 mt-12">
            © 2026 COGNIFY AI Inc. Built for Hackathon Excellence. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
