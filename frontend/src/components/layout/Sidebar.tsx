import React, { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import {
  LayoutDashboard,
  Dna,
  Compass,
  Target,
  Shuffle,
  Map,
  ClipboardCheck,
  Bot,
  FolderGit2,
  BarChart3,
  Activity,
  Settings,
  LogOut,
  Sparkles,
  User as UserIcon,
  PlayCircle,
} from "lucide-react";
import { useAuthContext } from "../../contexts/AuthContext";
import { GuidedTourModal } from "../demo/GuidedTourModal";

const NAV_ITEMS = [
  { label: "Overview", path: "/dashboard", icon: LayoutDashboard },
  { label: "My Skill DNA", path: "/skill-dna", icon: Dna },
  { label: "Career Explorer", path: "/careers", icon: Compass },
  { label: "Skill Gap Analysis", path: "/skill-gaps", icon: Target },
  { label: "Career Simulator", path: "/simulator", icon: Shuffle },
  { label: "Learning Roadmap", path: "/roadmap", icon: Map },
  { label: "Assessments", path: "/assessments", icon: ClipboardCheck },
  { label: "AI Mentor", path: "/mentor", icon: Bot },
  { label: "Project Verification", path: "/projects", icon: FolderGit2 },
  { label: "Analytics", path: "/analytics", icon: BarChart3 },
  { label: "Agent Center", path: "/agent-center", icon: Activity },
  { label: "Settings", path: "/settings", icon: Settings },
];

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthContext();
  const [tourOpen, setTourOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <>
      <GuidedTourModal isOpen={tourOpen} onClose={() => setTourOpen(false)} />
      <aside className="w-64 bg-slate-900 text-white flex flex-col shrink-0 border-r border-slate-800">
        {/* Brand Header */}
        <div className="p-4 border-b border-slate-800 flex items-center justify-center">
          <Link to="/dashboard" className="flex items-center gap-2">
            <img src="/logo.png" alt="COGNIFY AI" className="h-10 w-auto object-contain" />
          </Link>
        </div>

        {/* Interactive Guided Demo Button */}
        <div className="px-3 pt-3">
          <button
            onClick={() => setTourOpen(true)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-lg shadow-violet-600/30 border border-violet-400/30 transition transform hover:-translate-y-0.5"
          >
            <PlayCircle className="w-4 h-4 text-violet-200" />
            <span>Explore Alex's Journey</span>
          </button>
        </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Career Command
        </div>
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? "bg-gradient-to-r from-violet-600 to-indigo-600 text-white shadow-md shadow-violet-600/25"
                  : "text-slate-300 hover:text-white hover:bg-slate-800/60"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-white" : "text-slate-400"}`} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* User Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/40">
        <div className="flex items-center justify-between p-2 rounded-lg bg-slate-800/40 border border-slate-800">
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="w-8 h-8 rounded-full bg-violet-600/30 border border-violet-500/50 flex items-center justify-center text-violet-300 font-semibold text-xs">
              {user?.full_name?.charAt(0) || <UserIcon className="w-4 h-4" />}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-xs font-medium text-slate-200 truncate">{user?.full_name || "Alex Morgan"}</p>
              <p className="text-[10px] text-slate-400 truncate">{user?.email || "alex@cognify.ai"}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Log Out"
            className="p-1.5 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded transition"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}

