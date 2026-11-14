# COGNIFY AI — API Contract

## Base URL: /api

## Authentication
All protected routes require: `Authorization: Bearer <jwt_token>`
JWT contains: {sub: user_id, email, role, exp}

---

## Auth Endpoints

### POST /api/auth/register
Body: {email, username, password, full_name}
Response: {user: {id, email, username, full_name}, access_token}

### POST /api/auth/login
Body: {email, password}
Response: {user: {id, email, username, full_name}, access_token}

---

## Learner Endpoints

### GET /api/learner/profile
Response: {profile: {id, user_id, target_career, bio, education_level, years_experience, academic_background, certifications, career_readiness_score, skills: [{skill_id, name, proficiency, confidence, source}]}}

### PUT /api/learner/profile
Body: {bio?, education_level?, years_experience?, academic_background?, certifications?}
Response: {profile: updated_profile_object}

### POST /api/learner/skills
Body: {skills: [{skill_id, proficiency}]}
Response: {skills: [learner_skill_objects]}

---

## Career Endpoints

### GET /api/careers
Response: {careers: [{id, title, slug, description, category, demand_level}]}

### POST /api/career/analyze
Body: {career_id}  (uses authenticated learner)
Response: {analysis: {career, readiness_score, strong_skills, missing_skills, critical_gaps, recommendations, agent_activity}}

### POST /api/career/simulate
Body: {career_ids: [uuid, uuid, uuid]}
Response: {simulations: [{career, readiness, required_skills, missing_skills, effort_hours, transferable_skills}]}

### PUT /api/career/goal
Body: {career_id}
Response: {profile: updated, gap_analysis: {...}, new_roadmap: {...}}

---

## Skills Endpoints

### POST /api/skills/analyze
Body: {}  (uses authenticated learner profile data)
Response: {skill_analysis: {technical_skills, soft_skills, strengths, weaknesses, skill_dna: {categories}}}

### GET /api/skills/gaps
Query: ?career_id=uuid
Response: {gaps: [{skill, current_proficiency, required_proficiency, importance, gap, is_critical}]}

---

## Roadmap Endpoints

### POST /api/roadmap/generate
Body: {career_id}
Response: {roadmap: {id, title, tasks: [task_objects], total_hours, weeks}}

### GET /api/roadmap
Query: ?career_id=uuid
Response: {roadmap: roadmap_with_tasks}

### PUT /api/roadmap/tasks/{task_id}
Body: {status: "completed" | "in_progress" | "skipped"}
Response: {task: updated_task}

---

## Assessment Endpoints

### GET /api/assessments
Query: ?skill_id=uuid
Response: {assessments: [{id, title, skill, difficulty, time_limit, question_count}]}

### GET /api/assessments/{assessment_id}
Response: {assessment: {id, title, questions: [{id, question_text, question_type, options, topic, difficulty, points}]}}  
NOTE: correct_answer NOT included in response

### POST /api/assessments/submit
Body: {assessment_id, answers: {question_id: selected_answer}, time_taken_seconds}
Response: {result: {score, max_score, percentage, weak_topics, improvements, proficiency_updates, roadmap_changes}}

### GET /api/assessments/results
Query: ?skill_id=uuid
Response: {results: [result_objects]}

---

## Mentor Endpoints

### POST /api/mentor/chat
Body: {message, context?: "career" | "skill" | "assessment" | "general"}
Response: {response: {message, suggestions?, resources?}}

---

## Agent Endpoints

### POST /api/agents/orchestrate
Body: {workflow: "initial_analysis" | "assessment_update" | "career_change", params: {}}
Response: {result: {}, agent_activities: [activity_logs]}

### GET /api/agents/activity
Query: ?limit=50&learner_id=uuid
Response: {activities: [{id, agent_name, task, status, input_summary, output_summary, duration_ms, started_at, completed_at}]}

---

## Analytics Endpoints

### GET /api/analytics/dashboard
Response: {dashboard: {career_readiness, skills_mastered, total_skills, learning_progress, recent_assessments, upcoming_tasks, weekly_activity, recent_agent_decisions, recommendations}}

### GET /api/analytics/progress
Query: ?period=30d
Response: {progress: {skill_improvements: [], assessment_scores: [], readiness_history: [], activities_by_type: {}}}

---

## Projects Endpoints

### POST /api/projects/submit
Body: {title, description, technologies, github_url, outcomes}
Response: {project: {id, ..., demonstrated_skills, ai_analysis}}

### GET /api/projects
Response: {projects: [project_objects]}
