import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  ClipboardCheck,
  Clock,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  AlertTriangle,
  BrainCircuit,
  Bot,
  Sparkles,
} from "lucide-react";
import api from "../lib/api";

export function AssessmentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [assessment, setAssessment] = useState<any>(null);
  const [questions, setQuestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  // Quiz state
  const [currentIdx, setCurrentIdx] = useState(0);
  const [answers, setAnswers] = useState<{ [qId: string]: string }>({});
  const [timeLeft, setTimeLeft] = useState(25 * 60);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    async function loadAssessment() {
      try {
        const res = await api.get(`/assessments/${id}`);
        setAssessment(res.data.assessment);
        const qList = res.data.assessment.questions || [];
        setQuestions(qList);
        setTimeLeft((res.data.assessment.time_limit_minutes || 25) * 60);
      } catch (err) {
        console.error("Failed to load assessment details:", err);
      } finally {
        setLoading(false);
      }
    }
    loadAssessment();
  }, [id]);

  useEffect(() => {
    if (result || !timeLeft) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [result, timeLeft]);

  const handleSelectOption = (qId: string, option: string) => {
    setAnswers((prev) => ({ ...prev, [qId]: option }));
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    try {
      const res = await api.post("/assessments/submit", {
        assessment_id: id,
        answers: answers,
        time_taken_seconds: (assessment.time_limit_minutes || 25) * 60 - timeLeft,
      });
      setResult(res.data.result);
    } catch (err) {
      console.error("Submission failed:", err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Preparing Diagnostic Environment...</p>
        </div>
      </div>
    );
  }

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  // Result View
  if (result) {
    const pct = Number(result.percentage || 0);
    const isPoor = pct < 50;
    const adaptation = result.adaptation || {};
    const perfEval = adaptation.performance_evaluation || {};
    const mentorFeedback = adaptation.mentor_feedback || {};

    return (
      <div className="max-w-3xl mx-auto space-y-8 pb-12">
        <div className="p-8 rounded-3xl bg-white border border-slate-200 shadow-xl text-center">
          <div
            className={`w-16 h-16 rounded-2xl mx-auto flex items-center justify-center mb-4 ${
              isPoor ? "bg-red-50 text-red-600" : "bg-emerald-50 text-emerald-600"
            }`}
          >
            {isPoor ? <AlertTriangle className="w-8 h-8" /> : <CheckCircle2 className="w-8 h-8" />}
          </div>

          <h2 className="text-2xl font-bold text-slate-900 mb-1">Diagnostic Evaluation Complete</h2>
          <p className="text-xs text-slate-500 mb-6">
            Evaluated by COGNIFY Performance Agent and synchronized with your learning roadmap.
          </p>

          <div className="inline-flex items-center gap-6 p-4 rounded-2xl bg-slate-50 border border-slate-100 mb-8">
            <div>
              <div className="text-xs text-slate-400 uppercase font-semibold">Your Score</div>
              <div className="text-2xl font-extrabold text-slate-900 mt-0.5">
                {result.score} / {result.max_score}
              </div>
            </div>
            <div className="w-px h-8 bg-slate-200"></div>
            <div>
              <div className="text-xs text-slate-400 uppercase font-semibold">Percentage</div>
              <div className={`text-2xl font-extrabold mt-0.5 ${isPoor ? "text-red-600" : "text-emerald-600"}`}>
                {pct.toFixed(1)}%
              </div>
            </div>
            <div className="w-px h-8 bg-slate-200"></div>
            <div>
              <div className="text-xs text-slate-400 uppercase font-semibold">Updated Readiness</div>
              <div className="text-2xl font-extrabold text-violet-700 mt-0.5">
                {adaptation.new_career_readiness || 30.1}%
              </div>
            </div>
          </div>

          {/* Remedial Intervention Alert */}
          {isPoor && (
            <div className="p-5 rounded-2xl bg-amber-50/70 border border-amber-200 text-left mb-6">
              <div className="flex items-center gap-2 text-xs font-bold text-amber-900 mb-2">
                <AlertTriangle className="w-4 h-4 text-amber-600" />
                <span>Autonomous Learning Intervention Triggered</span>
              </div>
              <p className="text-xs text-amber-800 leading-relaxed mb-3">
                Score fell below the 50.0% competency threshold. The Performance Agent has isolated recurring conceptual weaknesses and automatically injected remedial tasks directly into Week 1 of your roadmap:
              </p>
              <div className="space-y-1.5">
                {(adaptation.adapted_tasks || []).map((t: string) => (
                  <div key={t} className="text-xs font-semibold text-amber-950 flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-600"></span>
                    <span>{t}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Mentor Briefing Card */}
          {mentorFeedback.message && (
            <div className="p-5 rounded-2xl bg-violet-50/60 border border-violet-100 text-left mb-6">
              <div className="flex items-center gap-2 text-xs font-bold text-violet-900 mb-2">
                <Bot className="w-4 h-4 text-violet-600" />
                <span>AI Career Mentor Post-Assessment Debrief</span>
              </div>
              <p className="text-xs text-violet-950 leading-relaxed mb-4">
                {mentorFeedback.message}
              </p>
              <div className="space-y-1 text-xs text-violet-900">
                <span className="font-bold">Next Steps Recommended:</span>
                {(mentorFeedback.suggestions || []).map((s: string, idx: number) => (
                  <div key={idx} className="flex items-center gap-1.5 text-violet-800">
                    <span className="text-violet-500">•</span> {s}
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex justify-center gap-4">
            <Link
              to="/roadmap"
              className="px-6 py-2.5 rounded-xl font-semibold bg-violet-600 hover:bg-violet-500 text-white text-xs shadow-md shadow-violet-600/20 transition flex items-center gap-2"
            >
              Inspect Adapted Roadmap <ArrowRight className="w-4 h-4" />
            </Link>
            <Link
              to="/assessments"
              className="px-6 py-2.5 rounded-xl font-medium bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs transition"
            >
              Back to Assessments
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const currentQ = questions[currentIdx];

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-12">
      {/* Quiz Header */}
      <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm flex items-center justify-between">
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-violet-600 px-2 py-0.5 rounded bg-violet-50">
            {assessment?.title || "Diagnostic Quiz"}
          </span>
          <div className="text-xs font-semibold text-slate-700 mt-1">
            Question {currentIdx + 1} of {questions.length}
          </div>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-100 font-mono text-xs font-semibold text-slate-800">
          <Clock className="w-3.5 h-3.5 text-slate-500" />
          <span>{formatTime(timeLeft)}</span>
        </div>
      </div>

      {/* Question Card */}
      {currentQ && (
        <div className="p-8 rounded-3xl bg-white border border-slate-200 shadow-sm space-y-6">
          <div>
            <div className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">
              Topic: {currentQ.topic || "General"}
            </div>
            <h3 className="text-lg font-bold text-slate-900 leading-snug">
              {currentQ.question_text}
            </h3>
          </div>

          {/* Options */}
          <div className="space-y-3">
            {(currentQ.options || []).map((opt: string) => {
              const isSelected = answers[currentQ.id] === opt;
              return (
                <button
                  key={opt}
                  type="button"
                  onClick={() => handleSelectOption(currentQ.id, opt)}
                  className={`w-full p-4 rounded-xl border text-left text-xs font-medium transition flex items-center justify-between ${
                    isSelected
                      ? "bg-violet-50 border-violet-600 text-violet-950 font-bold ring-2 ring-violet-500/20"
                      : "bg-slate-50/60 border-slate-200 text-slate-800 hover:border-slate-300 hover:bg-slate-50"
                  }`}
                >
                  <span>{opt}</span>
                  <div
                    className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                      isSelected ? "border-violet-600 bg-violet-600" : "border-slate-300"
                    }`}
                  >
                    {isSelected && <div className="w-1.5 h-1.5 rounded-full bg-white"></div>}
                  </div>
                </button>
              );
            })}
          </div>

          {/* Navigation Controls */}
          <div className="pt-6 border-t border-slate-100 flex items-center justify-between">
            <button
              type="button"
              disabled={currentIdx === 0}
              onClick={() => setCurrentIdx((prev) => prev - 1)}
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-600 hover:text-slate-900 disabled:opacity-40"
            >
              Previous
            </button>

            {currentIdx < questions.length - 1 ? (
              <button
                type="button"
                onClick={() => setCurrentIdx((prev) => prev + 1)}
                className="px-5 py-2.5 rounded-xl font-semibold bg-violet-600 hover:bg-violet-500 text-white text-xs shadow-md shadow-violet-600/20 transition flex items-center gap-1.5"
              >
                Next Question <ArrowRight className="w-3.5 h-3.5" />
              </button>
            ) : (
              <button
                type="button"
                disabled={submitting}
                onClick={handleSubmit}
                className="px-6 py-2.5 rounded-xl font-semibold bg-emerald-600 hover:bg-emerald-500 text-white text-xs shadow-md shadow-emerald-600/20 transition flex items-center gap-2 disabled:opacity-50"
              >
                {submitting ? "Evaluating..." : "Submit Assessment"}
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
