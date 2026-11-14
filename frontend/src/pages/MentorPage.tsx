import React, { useEffect, useState, useRef } from "react";
import {
  Bot,
  Send,
  Sparkles,
  ExternalLink,
  Target,
  BrainCircuit,
  Lightbulb,
  CheckCircle2,
  AlertTriangle,
  User as UserIcon,
} from "lucide-react";
import api from "../lib/api";

interface Message {
  id: string;
  sender: "user" | "mentor";
  text: string;
  suggestions?: string[];
  resources?: { title: string; url: string }[];
  timestamp: string;
}

export function MentorPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMsg, setInputMsg] = useState("");
  const [contextMode, setContextMode] = useState<string>("general");
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    async function loadLearnerContext() {
      try {
        const res = await api.get("/learner/profile");
        setProfile(res.data.profile);

        // Initial welcome message from Mentor using learner name
        const learnerName = res.data.profile?.user?.full_name || "Learner";
        const careerTitle = res.data.profile?.target_career?.title || "Full Stack Developer";
        const score = res.data.profile?.career_readiness_score || 0;

        setMessages([
          {
            id: "init-1",
            sender: "mentor",
            text: `Hello ${learnerName}! I am your COGNIFY AI Career Mentor for ${careerTitle}. I have continuous visibility into your Skill DNA, diagnostic test errors, and learning roadmap. Your estimated readiness is currently ${score}%. What would you like to deep-dive into today?`,
            suggestions: [
              "Why did I struggle on my last JavaScript assessment?",
              `What are the top 3 interview questions for ${careerTitle}?`,
              "Explain closures and lexical scoping simply",
              "Which skill gap should I prioritize next?",
            ],
            resources: [
              { title: "Roadmap.sh Engineering Guides", url: "https://roadmap.sh" },
              { title: "System Design Architecture Primer", url: "https://github.com/donnemartin/system-design-primer" },
            ],
            timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          },
        ]);
      } catch (err) {
        console.error("Failed to load mentor context:", err);
      }
    }
    loadLearnerContext();
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = textToSend || inputMsg;
    if (!text.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      sender: "user",
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!textToSend) setInputMsg("");
    setLoading(true);

    try {
      const res = await api.post("/mentor/chat", {
        message: text,
        context: contextMode,
      });

      const mentorRes = res.data.response || {};
      const mentorMessage: Message = {
        id: (Date.now() + 1).toString(),
        sender: "mentor",
        text: mentorRes.message || "I analyzed your question against your active competency profile.",
        suggestions: mentorRes.suggestions || [],
        resources: mentorRes.resources || [],
        timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, mentorMessage]);
    } catch (err) {
      console.error("Mentor chat error:", err);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          sender: "mentor",
          text: "I am temporarily offline or regenerating reasoning matrices. Please try again shortly.",
          timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
          <Bot className="w-3.5 h-3.5" />
          <span>Personalized AI Career Mentorship</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900">AI Career Mentor</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Dedicated 1-on-1 advisor equipped with your authentic assessment diagnostics and real-world market requirements.
        </p>
      </div>

      {/* Main Container: Chat Window (8 cols) + Real-Time Context Summary (4 cols) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[72vh]">
        {/* Chat Window (8 cols) */}
        <div className="lg:col-span-8 bg-white rounded-3xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
          {/* Top Context Mode Bar */}
          <div className="p-3.5 border-b border-slate-100 bg-slate-50/70 flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-medium text-slate-600">
              <span className="text-[11px] font-semibold text-slate-400 uppercase">Context Focus:</span>
              {["general", "career", "skill", "assessment"].map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setContextMode(mode)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium capitalize transition ${
                    contextMode === mode
                      ? "bg-violet-600 text-white shadow-sm"
                      : "bg-white text-slate-600 border border-slate-200 hover:bg-slate-100"
                  }`}
                >
                  {mode}
                </button>
              ))}
            </div>

            <div className="flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span>Mentor Connected</span>
            </div>
          </div>

          {/* Messages Scroll Area */}
          <div className="flex-1 p-5 overflow-y-auto space-y-4">
            {messages.map((m) => {
              const isUser = m.sender === "user";
              return (
                <div key={m.id} className={`flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
                  {!isUser && (
                    <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-600 text-white flex items-center justify-center shrink-0 shadow-md">
                      <Bot className="w-4 h-4" />
                    </div>
                  )}

                  <div className={`max-w-xl space-y-2 ${isUser ? "text-right" : "text-left"}`}>
                    <div
                      className={`p-4 rounded-2xl text-xs leading-relaxed inline-block ${
                        isUser
                          ? "bg-violet-600 text-white shadow-sm rounded-tr-none"
                          : "bg-slate-50 text-slate-800 border border-slate-200/80 rounded-tl-none"
                      }`}
                    >
                      <p className="whitespace-pre-wrap">{m.text}</p>
                    </div>

                    {/* Mentor Resource Recommendations */}
                    {m.resources && m.resources.length > 0 && (
                      <div className="space-y-1.5 pt-1">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">
                          Suggested Technical Material:
                        </span>
                        <div className="flex flex-wrap gap-2">
                          {m.resources.map((r, idx) => (
                            <a
                              key={idx}
                              href={r.url}
                              target="_blank"
                              rel="noreferrer"
                              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-violet-50 text-violet-700 border border-slate-200 text-[11px] font-medium transition"
                            >
                              <span>{r.title}</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Mentor Interactive Follow-Up Suggestions */}
                    {m.suggestions && m.suggestions.length > 0 && (
                      <div className="flex flex-wrap gap-1.5 pt-1">
                        {m.suggestions.map((s, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSendMessage(s)}
                            className="px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-100 hover:bg-violet-100 text-slate-700 hover:text-violet-800 border border-slate-200 transition"
                          >
                            💬 {s}
                          </button>
                        ))}
                      </div>
                    )}

                    <div className="text-[10px] text-slate-400 px-1">{m.timestamp}</div>
                  </div>

                  {isUser && (
                    <div className="w-8 h-8 rounded-xl bg-slate-200 text-slate-700 flex items-center justify-center shrink-0">
                      <UserIcon className="w-4 h-4" />
                    </div>
                  )}
                </div>
              );
            })}

            {loading && (
              <div className="flex items-center gap-3 text-xs text-slate-500">
                <div className="w-8 h-8 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center animate-spin">
                  <BrainCircuit className="w-4 h-4" />
                </div>
                <span>Mentor Agent synthesizing contextual response...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Chat Input Bar */}
          <div className="p-4 border-t border-slate-100 bg-white">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                handleSendMessage();
              }}
              className="flex items-center gap-2"
            >
              <input
                type="text"
                value={inputMsg}
                onChange={(e) => setInputMsg(e.target.value)}
                placeholder="Ask technical concept questions, interview strategies, or assessment explanations..."
                className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-2xl text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-violet-500"
              />
              <button
                type="submit"
                disabled={loading || !inputMsg.trim()}
                className="p-3 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-white rounded-2xl shadow-md shadow-violet-600/25 transition"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>

        {/* Real-Time Learner Context Inspector (4 cols) */}
        <div className="lg:col-span-4 bg-white rounded-3xl border border-slate-200 shadow-sm p-6 flex flex-col justify-between overflow-y-auto">
          <div>
            <h3 className="text-sm font-bold text-slate-900 mb-1 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-violet-600" /> Active Learner Context
            </h3>
            <p className="text-[11px] text-slate-500 mb-4">
              Real metrics visible to the Mentor Agent
            </p>

            <div className="space-y-4 text-xs">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Target Career Role</span>
                <span className="font-bold text-slate-800 text-sm">{profile?.target_career?.title || "Full Stack Developer"}</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Career Readiness</span>
                <div className="text-xl font-black text-violet-700">{profile?.career_readiness_score || 0}%</div>
              </div>

              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
                <span className="text-[10px] uppercase font-bold text-slate-400 block mb-2">Verified Competencies</span>
                <div className="flex flex-wrap gap-1.5">
                  {(profile?.skills || []).slice(0, 6).map((sk: any) => (
                    <span key={sk.skill_id} className="text-[10px] px-2 py-0.5 rounded bg-white border border-slate-200 font-medium text-slate-700">
                      {sk.name}: {sk.proficiency}%
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-slate-100 text-[11px] text-slate-400">
            Conversations are grounding in your actual diagnostic history, avoiding generic AI hallucinations.
          </div>
        </div>
      </div>
    </div>
  );
}
