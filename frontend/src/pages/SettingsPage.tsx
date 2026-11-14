import React, { useEffect, useState } from "react";
import { Settings, Save, CheckCircle2, User as UserIcon, Mail, Shield, AlertCircle, BrainCircuit } from "lucide-react";
import api from "../lib/api";
import { useAuthContext } from "../contexts/AuthContext";

export function SettingsPage() {
  const { user } = useAuthContext();
  const [bio, setBio] = useState("");
  const [educationLevel, setEducationLevel] = useState("");
  const [yearsExperience, setYearsExperience] = useState(1);
  const [academicBackground, setAcademicBackground] = useState("");
  const [certificationsInput, setCertificationsInput] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    async function loadProfile() {
      try {
        const res = await api.get("/learner/profile");
        const p = res.data.profile || {};
        setBio(p.bio || "");
        setEducationLevel(p.education_level || "");
        setYearsExperience(p.years_experience || 0);
        setAcademicBackground(p.academic_background || "");
        setCertificationsInput((p.certifications || []).join(", "));
      } catch (err) {
        console.error("Failed to load settings:", err);
      } finally {
        setLoading(false);
      }
    }
    loadProfile();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);
    try {
      const certs = certificationsInput.split(",").map((c) => c.trim()).filter(Boolean);
      await api.put("/learner/profile", {
        bio,
        education_level: educationLevel,
        years_experience: yearsExperience,
        academic_background: academicBackground,
        certifications: certs,
      });
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      console.error("Failed to save settings:", err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-10 h-10 rounded-xl bg-violet-600/20 text-violet-600 flex items-center justify-center mx-auto mb-4 animate-spin">
            <BrainCircuit className="w-5 h-5" />
          </div>
          <p className="text-xs font-medium text-slate-600">Loading User Settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl space-y-8 pb-12">
      {/* Header */}
      <div>
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-violet-100 text-violet-700 text-xs font-semibold mb-2">
          <Settings className="w-3.5 h-3.5" />
          <span>Learner Configuration</span>
        </div>
        <h1 className="text-2xl font-bold text-slate-900">User Settings & Profile</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Update profile parameters, academic credentials, and competency declarations.
        </p>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Profile configuration saved successfully and synchronized across agent models.</span>
        </div>
      )}

      {/* Account Info (Read-Only) */}
      <div className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-4">
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Account Credentials</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
            <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">Full Name</span>
            <span className="font-bold text-slate-800">{user?.full_name || "Alex Morgan"}</span>
          </div>
          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100">
            <span className="text-[10px] uppercase font-semibold text-slate-400 block mb-1">Email Address</span>
            <span className="font-bold text-slate-800">{user?.email || "alex@cognify.ai"}</span>
          </div>
        </div>
      </div>

      {/* Profile Form */}
      <form onSubmit={handleSave} className="p-6 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-5">
        <h2 className="text-sm font-bold text-slate-900 uppercase tracking-wider">Learner Bio & Background</h2>

        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1.5">
            Professional Summary / Bio
          </label>
          <textarea
            rows={3}
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            className="w-full p-3 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1.5">
              Education Level
            </label>
            <input
              type="text"
              value={educationLevel}
              onChange={(e) => setEducationLevel(e.target.value)}
              className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-violet-500"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1.5">
              Years of Experience: {yearsExperience}
            </label>
            <input
              type="range"
              min="0"
              max="15"
              value={yearsExperience}
              onChange={(e) => setYearsExperience(Number(e.target.value))}
              className="w-full accent-violet-600 mt-2"
            />
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1.5">
            Academic Background & Specialized Studies
          </label>
          <input
            type="text"
            value={academicBackground}
            onChange={(e) => setAcademicBackground(e.target.value)}
            className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1.5">
            Industry Certifications (Comma-separated)
          </label>
          <input
            type="text"
            value={certificationsInput}
            onChange={(e) => setCertificationsInput(e.target.value)}
            placeholder="AWS Certified Solutions Architect, Meta React Developer"
            className="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-900 focus:outline-none focus:ring-2 focus:ring-violet-500"
          />
        </div>

        <div className="pt-4 border-t border-slate-100 flex justify-end">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2.5 rounded-xl font-semibold bg-violet-600 hover:bg-violet-500 text-white text-xs shadow-md shadow-violet-600/20 transition flex items-center gap-2 disabled:opacity-50"
          >
            <Save className="w-4 h-4" />
            {saving ? "Updating..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}
