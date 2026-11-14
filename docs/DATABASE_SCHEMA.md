# COGNIFY AI — Database Schema Specification

## Python command
Use `python3.11` (located at `C:\Users\ASUS\.local\bin\python3.11.exe`) for ALL Python commands.
Use `python3.11 -m pip` for pip operations.

## Connection
- Use DATABASE_URL from environment variables
- Use SQLAlchemy async with asyncpg
- Connection pooling with pool_size=5, max_overflow=10

## All models use:
- UUID primary keys (uuid4)
- created_at / updated_at timestamps
- SQLAlchemy 2.0 mapped_column style

## Tables

### 1. users
```
id: UUID PK
email: String(255) UNIQUE NOT NULL
username: String(100) UNIQUE NOT NULL
password_hash: String(255) NOT NULL
full_name: String(200)
role: String(50) default="learner"  # learner, admin
is_active: Boolean default=True
created_at: DateTime
updated_at: DateTime
```

### 2. learner_profiles
```
id: UUID PK
user_id: UUID FK(users.id) UNIQUE NOT NULL
target_career_id: UUID FK(career_roles.id) NULLABLE
bio: Text
education_level: String(100)
years_experience: Integer default=0
academic_background: Text
certifications: JSON  # list of cert strings
career_readiness_score: Float default=0.0
last_analysis_at: DateTime NULLABLE
created_at: DateTime
updated_at: DateTime
```

### 3. skills
```
id: UUID PK
name: String(100) UNIQUE NOT NULL
category: String(50) NOT NULL  # technical, soft, tool
description: Text
is_active: Boolean default=True
created_at: DateTime
```

### 4. learner_skills
```
id: UUID PK
learner_id: UUID FK(learner_profiles.id) NOT NULL
skill_id: UUID FK(skills.id) NOT NULL
proficiency: Float default=0.0  # 0-100
confidence: String(50) default="claimed"  # claimed, assessed, demonstrated
source: String(50) default="self_reported"  # self_reported, assessment, project
last_assessed_at: DateTime NULLABLE
created_at: DateTime
updated_at: DateTime
UNIQUE(learner_id, skill_id)
```

### 5. career_roles
```
id: UUID PK
title: String(200) UNIQUE NOT NULL
slug: String(200) UNIQUE NOT NULL
description: Text
category: String(100)
avg_salary_range: String(100)
demand_level: String(50)  # high, medium, low
is_active: Boolean default=True
created_at: DateTime
```

### 6. career_requirements
```
id: UUID PK
career_id: UUID FK(career_roles.id) NOT NULL
skill_id: UUID FK(skills.id) NOT NULL
importance: Float NOT NULL  # 1-10 weight
min_proficiency: Float NOT NULL  # 0-100
is_critical: Boolean default=False
description: Text
created_at: DateTime
UNIQUE(career_id, skill_id)
```

### 7. learning_resources
```
id: UUID PK
skill_id: UUID FK(skills.id) NOT NULL
title: String(300) NOT NULL
resource_type: String(50) NOT NULL  # article, video, course, tutorial, documentation
url: String(500)
difficulty: String(50)  # beginner, intermediate, advanced
estimated_duration_hours: Float
description: Text
provider: String(200)
is_free: Boolean default=True
created_at: DateTime
```

### 8. learning_roadmaps
```
id: UUID PK
learner_id: UUID FK(learner_profiles.id) NOT NULL
career_id: UUID FK(career_roles.id) NOT NULL
title: String(300) NOT NULL
description: Text
total_estimated_hours: Float default=0
status: String(50) default="active"  # active, completed, archived
generated_by: String(50) default="ai"
created_at: DateTime
updated_at: DateTime
```

### 9. roadmap_tasks
```
id: UUID PK
roadmap_id: UUID FK(learning_roadmaps.id) NOT NULL
skill_id: UUID FK(skills.id) NOT NULL
title: String(300) NOT NULL
description: Text
topic: String(200)
difficulty: String(50)  # beginner, intermediate, advanced
estimated_hours: Float
learning_objective: Text
recommended_resource: Text
practical_exercise: Text
completion_criteria: Text
priority: Integer default=0
week_number: Integer
order_index: Integer
status: String(50) default="pending"  # pending, in_progress, completed, skipped
completed_at: DateTime NULLABLE
created_at: DateTime
updated_at: DateTime
```

### 10. assessments
```
id: UUID PK
skill_id: UUID FK(skills.id) NOT NULL
title: String(300) NOT NULL
description: Text
difficulty: String(50)
time_limit_minutes: Integer default=30
passing_score: Float default=70.0
is_active: Boolean default=True
created_at: DateTime
```

### 11. assessment_questions
```
id: UUID PK
assessment_id: UUID FK(assessments.id) NOT NULL
question_text: Text NOT NULL
question_type: String(50) NOT NULL  # multiple_choice, scenario, coding
options: JSON  # list of option strings
correct_answer: String(500) NOT NULL
explanation: Text
topic: String(200)
difficulty: String(50)
points: Float default=1.0
order_index: Integer
created_at: DateTime
```

### 12. assessment_results
```
id: UUID PK
learner_id: UUID FK(learner_profiles.id) NOT NULL
assessment_id: UUID FK(assessments.id) NOT NULL
score: Float NOT NULL
max_score: Float NOT NULL
percentage: Float NOT NULL
answers: JSON  # {question_id: selected_answer}
weak_topics: JSON  # list of weak topic strings
time_taken_seconds: Integer
completed_at: DateTime NOT NULL
created_at: DateTime
```

### 13. project_submissions
```
id: UUID PK
learner_id: UUID FK(learner_profiles.id) NOT NULL
title: String(300) NOT NULL
description: Text
technologies: JSON  # list of tech strings
github_url: String(500)
outcomes: Text
demonstrated_skills: JSON  # list of {skill_id, confidence}
ai_analysis: Text
status: String(50) default="submitted"  # submitted, analyzed
created_at: DateTime
updated_at: DateTime
```

### 14. agent_activity_logs
```
id: UUID PK
learner_id: UUID FK(learner_profiles.id) NULLABLE
agent_name: String(100) NOT NULL
task: String(300) NOT NULL
input_summary: Text
output_summary: Text
status: String(50) NOT NULL  # waiting, processing, completed, failed
error_message: Text
processing_duration_ms: Integer
execution_metadata: JSON
started_at: DateTime NOT NULL
completed_at: DateTime NULLABLE
created_at: DateTime
```

### 15. learning_activity
```
id: UUID PK
learner_id: UUID FK(learner_profiles.id) NOT NULL
activity_type: String(50) NOT NULL  # assessment, task_complete, skill_update, career_change, login
description: Text
metadata: JSON
created_at: DateTime
```

### 16. career_goal_history
```
id: UUID PK
learner_id: UUID FK(learner_profiles.id) NOT NULL
previous_career_id: UUID FK(career_roles.id) NULLABLE
new_career_id: UUID FK(career_roles.id) NOT NULL
readiness_at_change: Float
reason: Text
created_at: DateTime
```

