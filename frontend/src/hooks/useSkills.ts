import { useState, useEffect, useCallback } from "react";
import api from "../lib/api";
import type { LearnerSkill, SkillAnalysis, SkillGap } from "../types";

export function useSkills() {
  const [skills, setSkills] = useState<LearnerSkill[]>([]);
  const [analysis, setAnalysis] = useState<SkillAnalysis | null>(null);
  const [gaps, setGaps] = useState<SkillGap[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProfile = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get("/learner/profile");
      setSkills(res.data.profile.skills || []);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load skills");
    } finally {
      setLoading(false);
    }
  }, []);

  const analyzeSkills = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.post("/skills/analyze", {});
      setAnalysis(res.data.skill_analysis);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to analyze skills");
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchGaps = useCallback(async (careerId: string) => {
    try {
      setLoading(true);
      const res = await api.get(`/skills/gaps?career_id=${careerId}`);
      setGaps(res.data.gaps || []);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load skill gaps");
    } finally {
      setLoading(false);
    }
  }, []);

  const addSkills = useCallback(async (skillsToAdd: { skill_id: string; proficiency: number }[]) => {
    const res = await api.post("/learner/skills", { skills: skillsToAdd });
    setSkills(res.data.skills || []);
    return res.data.skills;
  }, []);

  useEffect(() => { fetchProfile(); }, [fetchProfile]);

  return { skills, analysis, gaps, loading, error, fetchProfile, analyzeSkills, fetchGaps, addSkills };
}
