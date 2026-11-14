import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles, ArrowRight, Lock, Mail, AlertCircle } from "lucide-react";
import { useAuthContext } from "../contexts/AuthContext";

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuthContext();
  const [email, setEmail] = useState("alex@cognify.ai");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Invalid email or password.");
    } finally {
      setLoading(false);
    }
  };

  const fillDemo = () => {
    setEmail("alex@cognify.ai");
    setPassword("password123");
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col justify-center py-12 sm:px-6 lg:px-8 selection:bg-violet-500 selection:text-white">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center space-x-2.5 mb-6">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-violet-500/30">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <span className="text-2xl font-bold tracking-tight text-white">
            COGNIFY <span className="text-violet-400 text-xs px-2 py-0.5 rounded bg-violet-950/80 border border-violet-800/60 font-semibold">AI</span>
          </span>
        </Link>
        <h2 className="text-2xl font-extrabold text-white">Welcome back</h2>
        <p className="mt-2 text-sm text-slate-400">
          Sign in to access your Career Command Center
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-slate-900 py-8 px-6 shadow-xl border border-slate-800 rounded-2xl sm:px-10">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-950/40 border border-red-800/50 flex items-center gap-2 text-red-300 text-xs">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Email Address
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="alex@cognify.ai"
                  className="block w-full pl-10 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                Password
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="block w-full pl-10 pr-3 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-violet-500 focus:border-transparent transition"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 rounded-xl text-sm font-semibold text-white bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 shadow-lg shadow-violet-600/30 transition flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {loading ? "Authenticating..." : "Sign In to Dashboard"}
              {!loading && <ArrowRight className="w-4 h-4" />}
            </button>
          </form>

          {/* Demo User Fast-Fill Button */}
          <div className="mt-6 pt-6 border-t border-slate-800">
            <button
              type="button"
              onClick={fillDemo}
              className="w-full py-2.5 px-3 rounded-xl text-xs font-medium bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700 text-violet-300 transition text-center"
            >
              Quick Fill Hackathon Demo: <strong>Alex Morgan</strong>
            </button>
          </div>

          <div className="mt-6 text-center text-xs text-slate-400">
            Don't have an account?{" "}
            <Link to="/register" className="text-violet-400 hover:text-violet-300 font-semibold">
              Create learner account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

