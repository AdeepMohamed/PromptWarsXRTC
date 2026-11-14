// ============ Auth ============
export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
}

// ============ Learner ============
export interface LearnerSkill {
  skill_id: string;
  name: string;
  proficiency: number;
  confidence: string;
  source: string;
}

export interface LearnerProfile {
  id: string;
  user_id: string;
  target_career: string | null;
  bio: string;
  education_level: string;
  years_experience: number;
  academic_background: string;
  certifications: string[];
  career_readiness_score: number;
  skills: LearnerSkill[];
}

// ============ Career ============
export interface Career {
  id: string;
  title: string;
  slug: string;
  description: string;
  category: string;
  demand_level: string;
}

export interface CareerAnalysis {
  career: Career;
  readiness_score: number;
  strong_skills: string[];
  missing_skills: string[];
  critical_gaps: string[];
  recommendations: string[];
  agent_activity: AgentActivity[];
}

export interface CareerSimulation {
  career: Career;
  readiness: number;
  required_skills: string[];
  missing_skills: string[];
  effort_hours: number;
  transferable_skills: string[];
}

// ============ Skills ============
export interface SkillAnalysis {
  technical_skills: LearnerSkill[];
  soft_skills: LearnerSkill[];
  strengths: string[];
  weaknesses: string[];
  skill_dna: { categories: SkillDNACategory[] };
}

export interface SkillDNACategory {
  name: string;
  value: number;
  fullMark: number;
}

export interface SkillGap {
  skill: string;
  current_proficiency: number;
  required_proficiency: number;
  importance: string;
  gap: number;
  is_critical: boolean;
}

// ============ Roadmap ============
export interface RoadmapTask {
  id: string;
  skill: string;
  topic: string;
  description: string;
  objective: string;
  resource: string;
  exercise: string;
  criteria: string;
  difficulty: string;
  estimated_hours: number;
  status: "pending" | "in_progress" | "completed" | "skipped";
  week_number: number;
  order: number;
}

export interface Roadmap {
  id: string;
  title: string;
  tasks: RoadmapTask[];
  total_hours: number;
  weeks: number;
}

// ============ Assessment ============
export interface AssessmentSummary {
  id: string;
  title: string;
  skill: string;
  difficulty: string;
  time_limit: number;
  question_count: number;
}

export interface AssessmentQuestion {
  id: string;
  question_text: string;
  question_type: string;
  options: string[];
  topic: string;
  difficulty: string;
  points: number;
}

export interface Assessment {
  id: string;
  title: string;
  questions: AssessmentQuestion[];
}

export interface AssessmentResult {
  score: number;
  max_score: number;
  percentage: number;
  weak_topics: string[];
  improvements: string[];
  proficiency_updates: Record<string, number>;
  roadmap_changes: string[];
}

// ============ Mentor ============
export interface MentorMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  suggestions?: string[];
  resources?: MentorResource[];
  timestamp: Date;
}

export interface MentorResource {
  title: string;
  url: string;
  type: string;
}

export interface MentorResponse {
  message: string;
  suggestions?: string[];
  resources?: MentorResource[];
}

// ============ Agent ============
export interface AgentActivity {
  id: string;
  agent_name: string;
  task: string;
  status: "waiting" | "processing" | "completed" | "failed";
  input_summary: string;
  output_summary: string;
  duration_ms: number;
  started_at: string;
  completed_at: string;
}

// ============ Analytics ============
export interface DashboardData {
  career_readiness: number;
  skills_mastered: number;
  total_skills: number;
  learning_progress: number;
  recent_assessments: { date: string; score: number; skill: string }[];
  upcoming_tasks: RoadmapTask[];
  weekly_activity: { day: string; hours: number }[];
  recent_agent_decisions: AgentActivity[];
  recommendations: string[];
}

export interface ProgressData {
  skill_improvements: { date: string; skill: string; proficiency: number }[];
  assessment_scores: { date: string; score: number; skill: string }[];
  readiness_history: { date: string; readiness: number }[];
  activities_by_type: Record<string, number>;
}

// ============ Projects ============
export interface Project {
  id: string;
  title: string;
  description: string;
  technologies: string[];
  github_url: string;
  outcomes: string;
  demonstrated_skills: string[];
  ai_analysis: string;
}
