"""
COGNIFY AI — Dedicated Idempotent Demo Data Seeder for Alex Morgan
Populates a complete, realistic 6-week learning journey across all tables:
- User (Alex Morgan)
- LearnerProfile (Week 4 In-Progress, Target: Full Stack Developer)
- LearnerSkills (Python 85%, SQL 75%, HTML 60%, CSS 45%, JS 25%, React 15%, Node 0%, Git 40%)
- 6-Week Learning Roadmap & 28 Tasks with Adaptive Remedial Intervention
- Assessments, Questions & Historical Assessment Results (85%, 78%, 88%, 45% failure)
- Project Submissions (Portfolio, Calculator, Task App) with Demonstration Evidence
- Agent Activity Logs across all 5 collaborating agents
- Learning Activities & Career Goal History
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal, _FallbackSessionLocal
from app.core.security import hash_password
from app.models.user import User
from app.models.learner import LearnerProfile, LearnerSkill
from app.models.skill import Skill
from app.models.career import CareerRole, CareerRequirement
from app.models.learning import LearningRoadmap, RoadmapTask, LearningResource
from app.models.assessment import Assessment, AssessmentQuestion, AssessmentResult
from app.models.project import ProjectSubmission
from app.models.agent import AgentActivityLog
from app.models.analytics import LearningActivity, CareerGoalHistory

DEMO_EMAIL = "alex@cognify.ai"
DEMO_NAME = "Alex Morgan"


async def seed_session(session, session_name="Database"):
    print(f"\n[Seeding {session_name}] Beginning idempotent Alex Morgan 6-week demo data setup...", flush=True)

    now = datetime.now(timezone.utc)
    week1_ago = now - timedelta(days=21)
    week2_ago = now - timedelta(days=14)
    week3_ago = now - timedelta(days=7)
    week4_ago = now - timedelta(days=2)

    # 1. Ensure Full Stack Developer Career exists
    c_res = await session.execute(select(CareerRole).where(CareerRole.slug == "full-stack-developer"))
    career_fs = c_res.scalar_one_or_none()
    if not career_fs:
        career_fs = CareerRole(
            id=uuid.uuid4(),
            title="Full Stack Developer",
            slug="full-stack-developer",
            description="End-to-end web engineer designing responsive UIs, scalable APIs, and robust databases.",
            salary_range_min=75000,
            salary_range_max=145000,
            market_demand="High",
            is_active=True,
            created_at=now,
        )
        session.add(career_fs)
        await session.flush()

    # 2. Get or Create User
    u_res = await session.execute(select(User).where(User.email == DEMO_EMAIL))
    user = u_res.scalar_one_or_none()
    if not user:
        user = User(
            id=uuid.uuid4(),
            email=DEMO_EMAIL,
            username="alex_morgan",
            password_hash=hash_password("password123"),
            full_name=DEMO_NAME,
            role="learner",
            is_active=True,
            created_at=week1_ago,
        )
        session.add(user)
        await session.flush()
    else:
        user.full_name = DEMO_NAME
        user.password_hash = hash_password("password123")

    # 3. Get or Create Learner Profile
    p_res = await session.execute(select(LearnerProfile).where(LearnerProfile.user_id == user.id))
    profile = p_res.scalar_one_or_none()
    if not profile:
        profile = LearnerProfile(
            id=uuid.uuid4(),
            user_id=user.id,
            target_career_id=career_fs.id,
            bio="Aspiring Full Stack Engineer currently on Week 4 of an intensive, adaptive learning journey.",
            education_level="Bachelor of Science in Computer Science",
            years_experience=2,
            academic_background="Undergraduate studies in CS; practical experience with Python data scripting and SQL queries.",
            certifications=[
                {"title": "Python for Everybody Specialization", "issuer": "Coursera", "year": 2024},
                {"title": "PostgreSQL Professional Fundamentals", "issuer": "Postgres Institute", "year": 2025},
            ],
            career_readiness_score=42.5,
            last_analysis_at=week4_ago,
            created_at=week1_ago,
        )
        session.add(profile)
        await session.flush()
    else:
        profile.target_career_id = career_fs.id
        profile.career_readiness_score = 42.5
        profile.years_experience = 2
        profile.last_analysis_at = week4_ago

    # 4. Skills Cache
    all_skills_res = await session.execute(select(Skill))
    skills_by_name = {s.name: s for s in all_skills_res.scalars().all()}

    # 5. Seed Alex's exact Skill Profile with Evidence
    demo_skills = [
        ("Python", 85.0, "demonstrated", "project_demonstrated"),
        ("SQL", 75.0, "assessed", "assessment_verified"),
        ("HTML", 60.0, "assessed", "assessment_verified"),
        ("CSS", 45.0, "demonstrated", "project_demonstrated"),
        ("JavaScript", 25.0, "assessed", "assessment_verified"),
        ("React", 15.0, "assessed", "assessment_verified"),
        ("Node.js", 0.0, "claimed", "self_reported"),
        ("Git", 40.0, "demonstrated", "project_demonstrated"),
    ]

    # Clean existing learner skills for Alex
    await session.execute(delete(LearnerSkill).where(LearnerSkill.learner_id == profile.id))
    for sname, prof, conf, src in demo_skills:
        sk = skills_by_name.get(sname)
        if sk:
            session.add(LearnerSkill(
                id=uuid.uuid4(),
                learner_id=profile.id,
                skill_id=sk.id,
                proficiency=prof,
                confidence=conf,
                source=src,
                last_assessed_at=week4_ago if prof > 0 else None,
                created_at=week1_ago,
            ))
    await session.flush()

    # 6. Seed 6-Week Roadmap & Tasks
    await session.execute(delete(RoadmapTask).where(RoadmapTask.roadmap_id.in_(
        select(LearningRoadmap.id).where(LearningRoadmap.learner_id == profile.id)
    )))
    await session.execute(delete(LearningRoadmap).where(LearningRoadmap.learner_id == profile.id))

    roadmap = LearningRoadmap(
        id=uuid.uuid4(),
        learner_id=profile.id,
        career_id=career_fs.id,
        title="Alex Morgan — 6-Week Adaptive Full Stack Roadmap",
        description="Comprehensive curriculum synthesizing frontend, backend, state management, and capstone deployment. Adapted on Week 4 after diagnostic assessment intervention.",
        total_estimated_hours=132,
        status="in_progress",
        created_at=week1_ago,
        updated_at=week4_ago,
    )
    session.add(roadmap)
    await session.flush()

    tasks_spec = [
        # Week 1 - COMPLETED
        ("HTML & CSS", "Semantic HTML & Page Architecture", "Structure accessible, SEO-optimized HTML documents.", "beginner", 4, "documentation", "Build an accessible blog layout", "Passes HTML5 validation", 1, 1, "completed", week1_ago + timedelta(days=2)),
        ("HTML & CSS", "CSS Flexbox & Responsive Layouts", "Master flex-direction, alignment, and mobile breakpoints.", "beginner", 6, "tutorial", "Create a responsive navigation bar and grid", "Responsive from 320px to 1440px", 1, 2, "completed", week1_ago + timedelta(days=4)),
        ("HTML & CSS", "CSS Grid & Modern Styling", "Implement complex 2D dashboard layouts with CSS Grid.", "intermediate", 5, "tutorial", "Build a multi-column pricing table", "Pixel-perfect across browsers", 1, 3, "completed", week1_ago + timedelta(days=6)),
        ("HTML & CSS", "Project: Personal Portfolio Website", "Develop and deploy a multi-page personal developer portfolio.", "intermediate", 8, "project", "Deploy portfolio on GitHub Pages/Vercel", "Live URL with responsive styling", 1, 4, "completed", week1_ago + timedelta(days=7)),

        # Week 2 - COMPLETED
        ("JavaScript", "Variables, Data Types & Scope", "Understand let/const, primitives, and block vs function scope.", "beginner", 4, "tutorial", "Refactor var-based scripts to modern ES6", "Zero global scope leaks", 2, 5, "completed", week2_ago + timedelta(days=2)),
        ("JavaScript", "Functions, Loops & Objects", "Implement modular functions, arrow syntax, and object manipulation.", "intermediate", 6, "tutorial", "Create a shopping cart total calculator", "Calculates discounts and taxes accurately", 2, 6, "completed", week2_ago + timedelta(days=4)),
        ("JavaScript", "DOM Manipulation & Event Handling", "Handle user clicks, keyboard events, and dynamic DOM mutation.", "intermediate", 5, "tutorial", "Build an interactive modal and accordion component", "Handles dynamic open/close smoothly", 2, 7, "completed", week2_ago + timedelta(days=6)),
        ("JavaScript", "Project: Interactive Calculator", "Build a feature-complete floating-point arithmetic calculator.", "intermediate", 7, "project", "Implement full arithmetic operations and display", "Accurate order of operations", 2, 8, "completed", week2_ago + timedelta(days=7)),

        # Week 3 - COMPLETED
        ("JavaScript", "ES6 Features & Array Methods", "Master map, filter, reduce, find, and destructuring syntax.", "intermediate", 4, "tutorial", "Process large JSON datasets with chaining", "Clean, functional code with 0 mutations", 3, 9, "completed", week3_ago + timedelta(days=2)),
        ("JavaScript", "Promises, Async/Await & Fetch API", "Write asynchronous network calls handling resolve/reject gracefully.", "intermediate", 6, "tutorial", "Fetch remote weather API data asynchronously", "Correct try/catch error boundaries", 3, 10, "completed", week3_ago + timedelta(days=4)),
        ("JavaScript", "API Integration & LocalStorage Persistence", "Store user preferences and retrieve state upon reload.", "advanced", 5, "tutorial", "Build an offline-first notes application", "Data survives page reloads", 3, 11, "completed", week3_ago + timedelta(days=6)),
        ("JavaScript", "Project: Task Management Application", "Develop a Kanban-style task board with drag-and-drop and persistence.", "intermediate", 8, "project", "Full CRUD operations on tasks", "Working drag-and-drop board with state", 3, 12, "completed", week3_ago + timedelta(days=7)),

        # Week 4 - IN PROGRESS (Adapted with Remedial Tasks!)
        ("React", "React Components, JSX & Props", "Understand component composition and unidirectional data flow.", "intermediate", 5, "course", "Build reusable UI component library (Button, Card, Input)", "Clean props validation", 4, 13, "completed", week4_ago),
        ("React", "Diagnostic: React Fundamentals Assessment", "Diagnostic evaluation of React core principles (Score: 45%).", "intermediate", 2, "assessment", "Complete 10 question conceptual diagnostic", "Identifies conceptual weaknesses", 4, 14, "completed", week4_ago),
        ("React", "[REMEDIAL] React State Management & useState Mastery", "Deep-dive into useState mechanics, immutability, and state lifting.", "intermediate", 4, "exercise", "Fix 5 broken stateful components with stale closure bugs", "Passes all state update assertions", 4, 15, "in_progress", None),
        ("React", "[REMEDIAL] useEffect Deep-Dive & Side-Effect Patterns", "Master dependency arrays, cleanup functions, and race-condition prevention.", "intermediate", 4, "exercise", "Refactor data-fetching effects to prevent memory leaks", "Zero unhandled side effects", 4, 16, "pending", None),
        ("React", "[REMEDIAL] Component Communication & Context API", "Eliminate prop drilling with React Context and custom hooks.", "intermediate", 3, "tutorial", "Implement global theme and auth context provider", "Working Context without unnecessary re-renders", 4, 17, "pending", None),
        ("React", "Project: React Analytics Dashboard", "Develop dynamic dashboard with charts, KPI cards, and filter state.", "intermediate", 8, "project", "Interactive charts with local state management", "Smooth rendering without state glitches", 4, 18, "pending", None),
        ("React", "Retake: React Diagnostic Assessment", "Demonstrate competency mastery after completing remedial sequence.", "intermediate", 2, "assessment", "Achieve >= 80% passing score", "Passing score verified", 4, 19, "pending", None),

        # Week 5 - UPCOMING
        ("Node.js", "Node.js Fundamentals & Event-Driven Architecture", "Understand V8 runtime, non-blocking I/O, and EventEmitter.", "intermediate", 5, "course", "Write custom CLI file processor using Node streams", "Processes 10MB file in chunks", 5, 20, "pending", None),
        ("Node.js", "Express.js RESTful API Architecture", "Design modular router, middleware pipelines, and error handlers.", "intermediate", 6, "tutorial", "Build REST endpoints for products and categories", "Strict HTTP status codes & JSON schema", 5, 21, "pending", None),
        ("Node.js", "Authentication & JWT Authorization", "Implement bcrypt password hashing, access/refresh tokens.", "advanced", 5, "tutorial", "Build auth middleware protecting private endpoints", "Secure token verification & expiration", 5, 22, "pending", None),
        ("Node.js", "Database Integration with PostgreSQL & Prisma", "Execute parameterized queries, relational joins, and migrations.", "advanced", 6, "tutorial", "Connect Express backend to Neon PostgreSQL database", "Handles ACID transactions reliably", 5, 23, "pending", None),
        ("Node.js", "Project: Task Management REST API", "Production-grade backend service with auth, filtering, and rate limiting.", "advanced", 10, "project", "Deploy REST API with Swagger documentation", "Passing Postman test suite", 5, 24, "pending", None),

        # Week 6 - UPCOMING
        ("Full Stack Integration", "Frontend-to-Backend Full Stack Wiring", "Connect React UI to Node.js backend using Axios interceptors.", "advanced", 8, "project", "Full CRUD synchronization between React and Express", "Zero CORS errors, seamless auth state", 6, 25, "pending", None),
        ("DevOps & Deployment", "Cloud Deployment on Render & Vercel", "Configure CI/CD pipelines, environment secrets, and custom domains.", "advanced", 6, "tutorial", "Deploy frontend to Vercel and backend to Render", "Automated deployment on git push", 6, 26, "pending", None),
        ("Testing", "Automated Testing Suite (Jest & Supertest)", "Write unit tests for UI components and integration tests for API.", "intermediate", 4, "tutorial", "Achieve > 80% code coverage on core routes", "All test suites passing in CI", 6, 27, "pending", None),
        ("Capstone", "Final Capstone: Complete Career Portfolio Platform", "Production-ready portfolio application demonstrating full stack mastery.", "advanced", 14, "project", "Publicly accessible web platform with live users", "Full stack verification certified", 6, 28, "pending", None),
    ]

    for sname, title, desc, diff, hours, rtype, exercise, criteria, wk, idx, status, comp_date in tasks_spec:
        # Resolve skill ID
        sk_match = None
        for k, v in skills_by_name.items():
            if k.lower() in sname.lower() or sname.lower() in k.lower():
                sk_match = v
                break
        if not sk_match:
            sk_match = list(skills_by_name.values())[0]

        session.add(RoadmapTask(
            id=uuid.uuid4(),
            roadmap_id=roadmap.id,
            skill_id=sk_match.id,
            title=title,
            description=desc,
            topic=sname,
            learning_objective=desc,
            difficulty=diff,
            estimated_hours=float(hours),
            recommended_resource="https://developer.mozilla.org" if "HTML" in sname or "CSS" in sname else "https://react.dev",
            practical_exercise=exercise,
            completion_criteria=criteria,
            priority=idx,
            order_index=idx,
            week_number=wk,
            status=status,
            completed_at=comp_date,
            created_at=week1_ago,
        ))
    await session.flush()

    # 7. Seed Diagnostic Assessments & Questions
    assessments_spec = [
        ("HTML and CSS Fundamentals", "HTML & CSS", "intermediate", 20, [
            ("What is the primary semantic benefit of using <main> over <div>?", "multiple_choice", ["Improves accessibility and document outline", "Increases styling speed", "Forces dark mode", "Compiles faster"], "Improves accessibility and document outline", "The <main> element specifies the main content of the document, allowing screen readers to jump directly to primary content.", "Semantic HTML", "beginner", 10),
            ("Which CSS display property establishes a 2-dimensional layout system?", "multiple_choice", ["display: grid", "display: flex", "display: block", "display: inline"], "display: grid", "CSS Grid is a 2D layout model handling both rows and columns simultaneously.", "CSS Grid", "intermediate", 10),
        ]),
        ("JavaScript Fundamentals", "JavaScript", "intermediate", 25, [
            ("Which statement about 'const' in ES6 is true?", "multiple_choice", ["It prevents reassigning the variable identifier", "It freezes object properties automatically", "It is hoisted without a temporal dead zone", "It cannot hold arrays"], "It prevents reassigning the variable identifier", "const creates an immutable binding, but the object contents can still be mutated.", "Variables & Scope", "beginner", 10),
            ("What does Array.prototype.map() return?", "multiple_choice", ["A new array with results of calling a function on each element", "The original mutated array", "A boolean flag", "The sum of elements"], "A new array with results of calling a function on each element", "map() creates a new array populated with the results of calling a provided function on every element in the calling array.", "Array Methods", "intermediate", 10),
        ]),
        ("Advanced JavaScript", "JavaScript", "advanced", 30, [
            ("What will an async function always return?", "multiple_choice", ["A Promise", "A callback function", "A generator", "Undefined"], "A Promise", "Async functions always return a Promise that resolves with the value returned by the function.", "Async/Await", "intermediate", 10),
            ("How do you prevent unhandled promise rejection in modern JS?", "multiple_choice", ["try/catch with await or .catch() handler", "Wrap in setTimeout", "Use eval()", "Define window.onerror only"], "try/catch with await or .catch() handler", "try/catch with async/await cleanly intercepts rejected promises.", "Error Handling", "advanced", 10),
        ]),
        ("React Fundamentals", "React", "intermediate", 20, [
            ("Why should state never be mutated directly in React?", "multiple_choice", ["React relies on shallow reference equality to schedule re-renders", "JavaScript throws a syntax error", "It deletes components", "It forces reload of page"], "React relies on shallow reference equality to schedule re-renders", "Direct mutation breaks reference comparisons, causing UI updates to be skipped.", "State Management", "intermediate", 10),
            ("What is the purpose of the dependency array in useEffect?", "multiple_choice", ["Controls when the effect executes based on value changes", "Lists imported packages", "Defines CSS rules", "Specifies component props"], "Controls when the effect executes based on value changes", "React compares current dependencies with previous ones to determine if the effect needs to re-run.", "React Hooks", "advanced", 10),
        ]),
        ("React Hooks and State Management", "React", "advanced", 25, [
            ("When should useReducer be preferred over useState?", "multiple_choice", ["When state transitions involve complex nested logic or multiple sub-values", "Only when building class components", "When making HTTP requests only", "Never"], "When state transitions involve complex nested logic or multiple sub-values", "useReducer provides predictable state updates via action dispatchers.", "State Management", "advanced", 10),
        ]),
        ("Node.js Fundamentals", "Node.js", "intermediate", 30, [
            ("How does Node.js achieve non-blocking asynchronous I/O?", "multiple_choice", ["Using libuv and the single-threaded event loop with thread pool delegation", "By running multiple Python processes", "Through hardware acceleration", "By blocking CPU cores"], "Using libuv and the single-threaded event loop with thread pool delegation", "The Node.js event loop handles concurrency by delegating I/O operations to the system kernel or thread pool.", "Event Loop", "intermediate", 10),
        ]),
    ]

    await session.execute(delete(AssessmentResult).where(AssessmentResult.learner_id == profile.id))

    for title, sname, diff, time_limit, questions in assessments_spec:
        sk_match = None
        for k, v in skills_by_name.items():
            if k.lower() in sname.lower() or sname.lower() in k.lower():
                sk_match = v
                break
        if not sk_match:
            sk_match = list(skills_by_name.values())[0]

        a_res = await session.execute(select(Assessment).where(Assessment.title == title))
        assessment = a_res.scalar_one_or_none()
        if not assessment:
            assessment = Assessment(
                id=uuid.uuid4(),
                skill_id=sk_match.id,
                title=title,
                description=f"Comprehensive diagnostic assessment evaluating {sname} competencies.",
                difficulty=diff,
                time_limit_minutes=time_limit,
                passing_score=70.0,
                is_active=True,
                created_at=week1_ago,
            )
            session.add(assessment)
            await session.flush()

            for qidx, (qtext, qtype, opts, corr, expl, topic, qdiff, pts) in enumerate(questions):
                session.add(AssessmentQuestion(
                    id=uuid.uuid4(),
                    assessment_id=assessment.id,
                    question_text=qtext,
                    question_type=qtype,
                    options=opts,
                    correct_answer=corr,
                    explanation=expl,
                    topic=topic,
                    difficulty=qdiff,
                    points=pts,
                    order_index=qidx + 1,
                    created_at=week1_ago,
                ))

        # Record Historical Assessment Results for completed tests
        if title == "HTML and CSS Fundamentals":
            session.add(AssessmentResult(
                id=uuid.uuid4(),
                assessment_id=assessment.id,
                learner_id=profile.id,
                score=17.0,
                max_score=20.0,
                percentage=85.0,
                weak_topics=[],
                time_taken_seconds=780,
                completed_at=week1_ago + timedelta(days=6),
            ))
        elif title == "JavaScript Fundamentals":
            session.add(AssessmentResult(
                id=uuid.uuid4(),
                assessment_id=assessment.id,
                learner_id=profile.id,
                score=15.6,
                max_score=20.0,
                percentage=78.0,
                weak_topics=["Variables & Scope"],
                time_taken_seconds=1020,
                completed_at=week2_ago + timedelta(days=6),
            ))
        elif title == "Advanced JavaScript":
            session.add(AssessmentResult(
                id=uuid.uuid4(),
                assessment_id=assessment.id,
                learner_id=profile.id,
                score=17.6,
                max_score=20.0,
                percentage=88.0,
                weak_topics=[],
                time_taken_seconds=1140,
                completed_at=week3_ago + timedelta(days=6),
            ))
        elif title == "React Fundamentals":
            # The Critical 45% Failure Scenario
            session.add(AssessmentResult(
                id=uuid.uuid4(),
                assessment_id=assessment.id,
                learner_id=profile.id,
                score=9.0,
                max_score=20.0,
                percentage=45.0,
                weak_topics=["React Hooks", "State Management", "Props", "Component Lifecycle"],
                time_taken_seconds=1200,
                completed_at=week4_ago,
            ))
    await session.flush()

    # 8. Seed Projects with Demonstration Evidence
    await session.execute(delete(ProjectSubmission).where(ProjectSubmission.learner_id == profile.id))
    projects_data = [
        (
            "Personal Portfolio Website",
            "Responsive multi-page portfolio highlighting projects, CV, and contact form with CSS Grid and semantic HTML.",
            "https://github.com/alexmorgan-dev/portfolio-website",
            ["HTML", "CSS", "JavaScript"],
            "Demonstrated clean semantic structuring, mobile responsiveness, and CSS flexbox styling. Verified by Skill Agent.",
            [
                {"skill": "HTML", "level": 60, "status": "verified"},
                {"skill": "CSS", "level": 45, "status": "verified"},
            ],
            True,
            week1_ago + timedelta(days=7),
        ),
        (
            "Interactive Calculator",
            "Floating-point interactive calculator with keyboard support, clear/delete buttons, and chained mathematical operations.",
            "https://github.com/alexmorgan-dev/js-calculator",
            ["JavaScript", "HTML", "CSS"],
            "Demonstrated DOM event listeners, expression parsing, and edge-case division-by-zero handling. Verified by Skill Agent.",
            [
                {"skill": "JavaScript", "level": 50, "status": "verified"},
                {"skill": "DOM Manipulation", "level": 55, "status": "verified"},
            ],
            True,
            week2_ago + timedelta(days=7),
        ),
        (
            "Task Management Application",
            "Client-side Kanban task board featuring priority filters, local storage serialization, and real-time status transitions.",
            "https://github.com/alexmorgan-dev/task-management-app",
            ["JavaScript", "LocalStorage", "ES6"],
            "Demonstrated async data operations, ES6 array methods, and local storage state persistence. Under verification.",
            [
                {"skill": "JavaScript", "level": 65, "status": "pending_inspection"},
            ],
            False,
            week3_ago + timedelta(days=7),
        ),
    ]

    for ptitle, pdesc, gh_url, techs, eval_notes, demonstrated, is_ver, sub_date in projects_data:
        session.add(ProjectSubmission(
            id=uuid.uuid4(),
            learner_id=profile.id,
            title=ptitle,
            description=pdesc,
            github_url=gh_url,
            technologies=techs,
            outcomes=eval_notes,
            ai_analysis=eval_notes,
            demonstrated_skills=demonstrated,
            status="verified" if is_ver else "submitted",
            created_at=sub_date,
        ))
    await session.flush()

    # 9. Seed Agent Activity Logs representing the 6-week journey
    await session.execute(delete(AgentActivityLog).where(AgentActivityLog.learner_id == profile.id))

    logs_data = [
        (
            "skill_agent",
            "Initial Skill DNA Extraction",
            "Learner self-reported: Python (85%), SQL (75%), HTML (40%), CSS (20%). Zero practical JS/React claims.",
            "Identified strong backend data fundamentals (Python, SQL). Flagged critical frontend deficit (JavaScript 0%, React 0%).",
            "completed",
            120,
            {
                "skill_dna": {"programming": 65, "analytical_thinking": 70, "problem_solving": 60, "communication": 50, "technical_proficiency": 55, "project_experience": 40},
                "strengths": ["Python", "SQL"],
                "weaknesses": ["JavaScript", "React", "Node.js"],
            },
            week1_ago,
        ),
        (
            "career_agent",
            "Full Stack Readiness Analysis",
            "Target role: Full Stack Developer. Compared 8 core competencies against Neon PostgreSQL role benchmarks.",
            "Initial Career Readiness: 24.4%. Critical gaps: JavaScript, React, Node.js. Transferable: Python, SQL.",
            "completed",
            145,
            {"readiness": 24.4, "critical_gaps": ["JavaScript", "React", "Node.js"]},
            week1_ago + timedelta(minutes=2),
        ),
        (
            "learning_agent",
            "Synthesize 6-Week Learning Roadmap",
            "Input: Skill gaps, target career 'Full Stack Developer', duration 6 weeks, prerequisite graph.",
            "Synthesized 28 dependency-sequenced tasks across 6 progressive milestone weeks with portfolio deliverables.",
            "completed",
            320,
            {"weeks": 6, "total_tasks": 28, "milestones": ["Portfolio", "Calculator", "Task App", "React Dashboard", "REST API", "Full Stack Capstone"]},
            week1_ago + timedelta(minutes=4),
        ),
        (
            "mentor_agent",
            "Curate Weekly Guidance & Project Focus",
            "Read initial roadmap and gap analysis. Formulated advice for Week 1 HTML/CSS foundation.",
            "Recommended prioritizing Semantic HTML and Flexbox layouts. Suggested building Personal Portfolio site.",
            "completed",
            95,
            {"recommendation": "Master CSS Flexbox and semantic layout before moving to JavaScript."},
            week1_ago + timedelta(minutes=6),
        ),
        (
            "performance_agent",
            "Diagnostic Evaluation: Week 4 React Fundamentals",
            "Assessment submission: Score 45% (9/20 points). Time spent: 20 minutes.",
            "DIAGNOSTIC FAILURE DETECTED. Conceptual breakdown: React Hooks (30%), State Management (25%), Component Lifecycle (40%).",
            "completed",
            180,
            {
                "score": 45.0,
                "passed": False,
                "weak_concepts": ["React Hooks", "State Management", "Props", "Component Lifecycle"],
                "action": "Triggered Autonomous Remediation Protocol",
            },
            week4_ago,
        ),
        (
            "skill_agent",
            "Recalibrate Skill DNA Post-Assessment",
            "Performance Agent signal: React diagnostic failure (45%). Updated evidence confidence to 'assessed'.",
            "React proficiency updated to 15%. Skill DNA technical proficiency adjusted to 52%.",
            "completed",
            110,
            {"skill": "React", "old_prof": 0, "new_prof": 15, "confidence": "assessed"},
            week4_ago + timedelta(seconds=15),
        ),
        (
            "career_agent",
            "Recompute Career Readiness Post-Diagnostic",
            "Updated React proficiency (15%). Recalculated weighted readiness score.",
            "Full Stack Developer Readiness updated to 42.5%. React remains #1 priority gap.",
            "completed",
            135,
            {"readiness": 42.5, "delta": "+18.1% since onboarding"},
            week4_ago + timedelta(seconds=30),
        ),
        (
            "learning_agent",
            "Autonomous Roadmap Remediation Injection",
            "Notification from Performance Agent: Weakness in React Hooks and state management.",
            "AUTONOMOUS INTERVENTION: Injected 3 targeted practice modules into Week 4 roadmap: useState Mastery, useEffect Side-Effects, and Context API.",
            "completed",
            290,
            {"injected_tasks": ["[REMEDIAL] React State Management", "[REMEDIAL] useEffect Deep-Dive", "[REMEDIAL] Component Communication"]},
            week4_ago + timedelta(seconds=45),
        ),
        (
            "mentor_agent",
            "Formulate Targeted Remediation Advice",
            "Context: 45% React score, weak hooks understanding, adapted Week 4 tasks.",
            "Prepared personalized coaching message explaining why useState/useEffect struggle occurred and how the remedial exercises will bridge the gap.",
            "completed",
            115,
            {"mentor_intervention": "Advised building Task App state before starting Node.js backend."},
            week4_ago + timedelta(minutes=1),
        ),
    ]

    for aname, task, in_sum, out_sum, status, dur, meta, log_date in logs_data:
        session.add(AgentActivityLog(
            id=uuid.uuid4(),
            learner_id=profile.id,
            agent_name=aname,
            task=task,
            input_summary=in_sum,
            output_summary=out_sum,
            status=status,
            processing_duration_ms=dur,
            execution_metadata=meta,
            started_at=log_date,
            completed_at=log_date + timedelta(milliseconds=dur),
            created_at=log_date,
        ))
    await session.flush()

    # 10. Seed Learning Activities for Analytics charts
    await session.execute(delete(LearningActivity).where(LearningActivity.learner_id == profile.id))
    activities_data = [
        ("task_complete", "Completed Week 1 Task: Semantic HTML & Page Architecture", week1_ago + timedelta(days=2)),
        ("task_complete", "Completed Week 1 Task: CSS Flexbox & Responsive Layouts", week1_ago + timedelta(days=4)),
        ("project_submit", "Submitted Project: Personal Portfolio Website (Verified demo evidence)", week1_ago + timedelta(days=7)),
        ("assessment", "Completed HTML and CSS Fundamentals Assessment with score 85%", week1_ago + timedelta(days=6)),
        ("task_complete", "Completed Week 2 Task: Variables, Data Types & Scope", week2_ago + timedelta(days=2)),
        ("project_submit", "Submitted Project: Interactive Calculator (Verified demo evidence)", week2_ago + timedelta(days=7)),
        ("assessment", "Completed JavaScript Fundamentals Assessment with score 78%", week2_ago + timedelta(days=6)),
        ("task_complete", "Completed Week 3 Task: Promises, Async/Await & Fetch API", week3_ago + timedelta(days=4)),
        ("assessment", "Completed Advanced JavaScript Assessment with score 88%", week3_ago + timedelta(days=6)),
        ("assessment", "Submitted React Fundamentals Assessment with score 45%. System triggered Remedial Intervention.", week4_ago),
        ("roadmap_adapted", "Learning roadmap autonomously adapted based on diagnostic assessment performance.", week4_ago + timedelta(seconds=45)),
    ]

    for atype, adesc, adate in activities_data:
        session.add(LearningActivity(
            id=uuid.uuid4(),
            learner_id=profile.id,
            activity_type=atype,
            description=adesc,
            activity_metadata={"source": "demo_seed"},
            created_at=adate,
        ))

    await session.commit()
    print(f"SUCCESS: Alex Morgan 6-week demo data populated in {session_name}!", flush=True)


async def main():
    # 1. Seed fallback local DB (guaranteed speed & offline presentation)
    try:
        async with _FallbackSessionLocal() as session:
            await seed_session(session, "Local High-Speed Database (cognify.db)")
    except Exception as e:
        print(f"Error seeding local database: {e}", flush=True)

    # 2. Seed primary Neon PostgreSQL database
    try:
        async with AsyncSessionLocal() as session:
            await seed_session(session, "Neon Serverless PostgreSQL")
    except Exception as e:
        print(f"Note on Neon PostgreSQL seeding (network fallback active): {e}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
