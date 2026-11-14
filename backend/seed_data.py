"""
Seed script for COGNIFY AI.

Populates the database with:
- 35+ technical & soft skills
- 9 career roles (Full Stack Developer, AI Engineer, ML Engineer, Data Scientist, Data Analyst,
  Cybersecurity Analyst, Cloud Engineer, DevOps Engineer, UI/UX Designer)
- Detailed career skill requirements with weights & thresholds
- High-quality learning resources
- Robust assessment questions for JavaScript, Python, React, SQL, HTML/CSS
- Sample learner: Alex Morgan (alex@cognify.ai / password123) with the demo skills profile.
"""

import asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from app.core.database import AsyncSessionLocal, init_db
from app.core.security import hash_password
from app.models.user import User
from app.models.learner import LearnerProfile, LearnerSkill
from app.models.skill import Skill
from app.models.career import CareerRole, CareerRequirement
from app.models.learning import LearningResource
from app.models.assessment import Assessment, AssessmentQuestion


SKILLS_DATA = [
    # Technical Frontend
    ("JavaScript", "technical", "Dynamic programming language for web client and server development"),
    ("TypeScript", "technical", "Typed superset of JavaScript that compiles to plain JavaScript"),
    ("React", "technical", "Component-based declarative UI library for web development"),
    ("HTML", "technical", "Standard markup language for web page structure and semantics"),
    ("CSS", "technical", "Style sheet language for presentation, layout, and responsive UI"),
    ("Tailwind CSS", "technical", "Utility-first CSS framework for rapid UI styling"),
    ("Next.js", "technical", "Full-stack React framework with SSR and server components"),
    ("Vue.js", "technical", "Progressive JavaScript framework for building user interfaces"),

    # Technical Backend & Systems
    ("Python", "technical", "High-level programming language for web, data, and AI systems"),
    ("Node.js", "technical", "V8 asynchronous event-driven JavaScript runtime environment"),
    ("FastAPI", "technical", "High-performance Python web framework based on type hints"),
    ("Django", "technical", "High-level Python web framework for rapid, secure development"),
    ("SQL", "technical", "Standard language for storing, manipulating and retrieving relational data"),
    ("PostgreSQL", "technical", "Advanced open-source object-relational database system"),
    ("MongoDB", "technical", "Document-oriented NoSQL database system"),
    ("Redis", "technical", "In-memory data store used as database, cache, and message broker"),

    # AI, ML & Data
    ("Machine Learning", "technical", "Algorithms that improve automatically through experience and data"),
    ("Deep Learning", "technical", "Neural network architectures with multiple representation layers"),
    ("PyTorch", "technical", "Deep learning framework for tensor computation and neural networks"),
    ("TensorFlow", "technical", "End-to-end open source platform for machine learning"),
    ("Data Analysis", "technical", "Inspecting, cleansing, transforming, and modeling data"),
    ("Pandas", "technical", "Fast, powerful data analysis and manipulation library for Python"),
    ("NumPy", "technical", "Fundamental package for scientific computing with Python arrays"),
    ("Scikit-Learn", "technical", "Simple and efficient tools for predictive data analysis"),
    ("Data Visualization", "technical", "Visual representation of data with charts, plots, and graphs"),

    # Cloud, DevOps & Security
    ("Git", "technical", "Distributed version control system for tracking source code changes"),
    ("Docker", "technical", "Platform for building, shipping, and running containers"),
    ("Kubernetes", "technical", "Automated container orchestration and cluster management system"),
    ("AWS", "technical", "Amazon Web Services on-demand cloud computing platforms"),
    ("CI/CD", "technical", "Continuous Integration and Continuous Delivery automated pipelines"),
    ("Linux", "technical", "Open-source Unix-like operating system kernel and shell"),
    ("Cybersecurity Fundamentals", "technical", "Protecting systems, networks, and programs from digital attacks"),
    ("Network Security", "technical", "Measures to protect the usability and integrity of network data"),

    # Design & Soft Skills
    ("UI Design", "technical", "Designing graphical user interfaces and visual aesthetics"),
    ("UX Research", "technical", "Systematic study of target users to inform product design"),
    ("Figma", "tool", "Collaborative cloud-based interface design tool"),
    ("Problem Solving", "soft", "Analytical ability to diagnose issues and engineer optimal solutions"),
    ("Communication", "soft", "Conveying technical and architectural concepts clearly to teams"),
    ("Critical Thinking", "soft", "Disciplined evaluation and synthesis of evidence and requirements"),
    ("Team Collaboration", "soft", "Working effectively in cross-functional product and agile squads"),
    ("Project Management", "soft", "Planning, organizing, and managing tasks to achieve milestones"),
]

CAREERS_DATA = [
    {
        "title": "Full Stack Developer",
        "slug": "full-stack-developer",
        "category": "Software Engineering",
        "demand_level": "high",
        "avg_salary_range": "$95,000 - $145,000",
        "description": "Architects and implements complete web applications spanning responsive frontends, scalable REST/GraphQL APIs, and robust relational databases.",
        "requirements": [
            ("JavaScript", 10.0, 75.0, True, "Essential core runtime of modern web architectures"),
            ("React", 9.0, 70.0, True, "Primary frontend UI framework required for interactive client features"),
            ("HTML", 7.0, 80.0, False, "Semantic markup foundation for accessible document hierarchies"),
            ("CSS", 7.0, 75.0, False, "Design layouts, flexbox, grid, and responsive styling"),
            ("Python", 8.0, 70.0, False, "Backend service layer and API development"),
            ("Node.js", 8.0, 65.0, False, "Backend server execution and tooling"),
            ("SQL", 9.0, 75.0, True, "Relational data modeling, indexing, and transactional queries"),
            ("Git", 8.0, 70.0, True, "Version control, branching strategies, and collaborative pull requests"),
            ("Problem Solving", 8.0, 70.0, False, "Debugging complex full-stack data flows"),
        ]
    },
    {
        "title": "Data Scientist",
        "slug": "data-scientist",
        "category": "Data & AI",
        "demand_level": "high",
        "avg_salary_range": "$110,000 - $160,000",
        "description": "Transforms unstructured and tabular data into predictive insights using statistical modeling, machine learning, and advanced visual storytelling.",
        "requirements": [
            ("Python", 10.0, 85.0, True, "Primary programming language for data pipelines and modeling"),
            ("SQL", 9.0, 80.0, True, "Complex database querying, window functions, and data warehousing"),
            ("Data Analysis", 9.0, 80.0, True, "Exploratory data analysis and hypothesis testing"),
            ("Pandas", 9.0, 80.0, True, "Data wrangling, cleaning, and matrix manipulations"),
            ("Machine Learning", 9.0, 75.0, True, "Supervised and unsupervised predictive algorithms"),
            ("Data Visualization", 8.0, 70.0, False, "Executive dashboards and communicating insights"),
            ("Critical Thinking", 8.0, 75.0, False, "Rigorous formulation of business hypotheses"),
            ("Git", 7.0, 60.0, False, "Reproducible research and model versioning"),
        ]
    },
    {
        "title": "AI Engineer",
        "slug": "ai-engineer",
        "category": "Data & AI",
        "demand_level": "high",
        "avg_salary_range": "$130,000 - $185,000",
        "description": "Builds and deploys production-grade AI agent systems, fine-tuned foundational models, LLM pipelines, and neural networks at scale.",
        "requirements": [
            ("Python", 10.0, 90.0, True, "Fundamental runtime for AI libraries and agent orchestration"),
            ("Deep Learning", 9.0, 80.0, True, "Neural network architectures, transformers, and loss optimization"),
            ("PyTorch", 9.0, 75.0, True, "Framework for model training, embeddings, and fine-tuning"),
            ("FastAPI", 8.0, 75.0, False, "Serving high-throughput model endpoints and streaming responses"),
            ("Docker", 8.0, 70.0, False, "Containerizing inference environments and dependencies"),
            ("Git", 8.0, 70.0, False, "Code versioning and model repository collaboration"),
            ("Problem Solving", 9.0, 80.0, True, "Mathematical debugging of model convergence and latent space"),
        ]
    },
    {
        "title": "Machine Learning Engineer",
        "slug": "machine-learning-engineer",
        "category": "Data & AI",
        "demand_level": "high",
        "avg_salary_range": "$125,000 - $175,000",
        "description": "Bridges the gap between data science prototypes and production scale, building MLOps pipelines and real-time inference engines.",
        "requirements": [
            ("Python", 10.0, 85.0, True, "Primary ML development language"),
            ("Machine Learning", 10.0, 85.0, True, "Core algorithms, validation strategies, and hyperparameter tuning"),
            ("Docker", 9.0, 75.0, True, "Containerization of training pipelines"),
            ("SQL", 8.0, 75.0, False, "Feature store and training dataset retrieval"),
            ("CI/CD", 8.0, 70.0, False, "Continuous deployment of model pipelines"),
        ]
    },
    {
        "title": "Data Analyst",
        "slug": "data-analyst",
        "category": "Data & Analytics",
        "demand_level": "medium",
        "avg_salary_range": "$75,000 - $105,000",
        "description": "Interprets business metrics, designs executive dashboards, and delivers actionable commercial intelligence through SQL and visual tools.",
        "requirements": [
            ("SQL", 10.0, 85.0, True, "Core skill for pulling, grouping, and aggregating business records"),
            ("Data Analysis", 9.0, 80.0, True, "Metric definition and trend discovery"),
            ("Data Visualization", 9.0, 80.0, True, "Presenting findings cleanly to stakeholders"),
            ("Python", 7.0, 60.0, False, "Automating recurring reporting scripts"),
            ("Communication", 9.0, 80.0, True, "Explaining analytical insights to leadership"),
        ]
    },
    {
        "title": "Cloud Engineer",
        "slug": "cloud-engineer",
        "category": "Infrastructure",
        "demand_level": "high",
        "avg_salary_range": "$105,000 - $155,000",
        "description": "Designs, secures, and maintains cloud infrastructure, serverless architectures, and reliable cloud networking on AWS and GCP.",
        "requirements": [
            ("AWS", 10.0, 80.0, True, "Primary cloud infrastructure services (EC2, S3, RDS, Lambda)"),
            ("Docker", 9.0, 75.0, True, "Containerized workloads"),
            ("Linux", 9.0, 75.0, True, "OS management, bash scripting, and permissions"),
            ("CI/CD", 8.0, 70.0, False, "Infrastructure as code and deployment automation"),
            ("Python", 7.0, 65.0, False, "Cloud automation and serverless lambdas"),
        ]
    },
    {
        "title": "DevOps Engineer",
        "slug": "devops-engineer",
        "category": "Infrastructure",
        "demand_level": "high",
        "avg_salary_range": "$115,000 - $165,000",
        "description": "Automates release engineering, orchestrates Kubernetes clusters, and implements robust site reliability and observability pipelines.",
        "requirements": [
            ("Docker", 10.0, 85.0, True, "Foundational container platform"),
            ("Kubernetes", 10.0, 80.0, True, "Cluster orchestration and zero-downtime rollouts"),
            ("CI/CD", 10.0, 85.0, True, "Automated build, test, and release pipelines"),
            ("Linux", 9.0, 80.0, True, "Server administration and performance debugging"),
            ("Git", 9.0, 80.0, True, "GitOps workflow and repository management"),
        ]
    },
    {
        "title": "Cybersecurity Analyst",
        "slug": "cybersecurity-analyst",
        "category": "Security",
        "demand_level": "high",
        "avg_salary_range": "$100,000 - $150,000",
        "description": "Monitors systems for intrusions, assesses vulnerabilities, implements zero-trust policies, and responds to active digital threats.",
        "requirements": [
            ("Cybersecurity Fundamentals", 10.0, 85.0, True, "Security principles, threat vectors, and defense-in-depth"),
            ("Network Security", 9.0, 80.0, True, "Firewalls, packet inspection, and secure protocols"),
            ("Linux", 8.0, 75.0, True, "System auditing and forensic log inspection"),
            ("Problem Solving", 9.0, 80.0, True, "Incident triage under pressure"),
        ]
    },
    {
        "title": "UI/UX Designer",
        "slug": "ui-ux-designer",
        "category": "Design",
        "demand_level": "medium",
        "avg_salary_range": "$85,000 - $130,000",
        "description": "Designs intuitive user journeys, wireframes, design systems, and high-fidelity interactive prototypes in Figma.",
        "requirements": [
            ("Figma", 10.0, 85.0, True, "Industry standard prototype and design tool"),
            ("UI Design", 10.0, 85.0, True, "Typography, visual hierarchy, spacing, and micro-interactions"),
            ("UX Research", 9.0, 80.0, True, "User interviews, usability testing, and persona mapping"),
            ("HTML", 6.0, 50.0, False, "Understanding web technical constraints"),
            ("CSS", 6.0, 50.0, False, "Understanding layout models and responsive breakpoints"),
        ]
    },
]

ASSESSMENTS_DATA = [
    {
        "skill": "JavaScript",
        "title": "JavaScript Core Concepts & Runtime Diagnostic",
        "difficulty": "intermediate",
        "time_limit": 25,
        "questions": [
            {
                "question": "What is the output of `typeof null` in standard JavaScript?",
                "type": "multiple_choice",
                "options": ["'object'", "'null'", "'undefined'", "'boolean'"],
                "correct": "'object'",
                "explanation": "In JavaScript, typeof null returns 'object' due to a historical legacy implementation bug in the first version of JS.",
                "topic": "Variables and Data Types",
                "difficulty": "beginner",
                "points": 1.0,
            },
            {
                "question": "Which keyword prevents variables from being re-assigned and exhibits block-scope behavior?",
                "type": "multiple_choice",
                "options": ["const", "var", "let", "static"],
                "correct": "const",
                "explanation": "const declarations are block-scoped and cannot be reassigned after declaration.",
                "topic": "Scope and Declarations",
                "difficulty": "beginner",
                "points": 1.0,
            },
            {
                "question": "How does JavaScript handle asynchronous operations under the hood despite being single-threaded?",
                "type": "multiple_choice",
                "options": [
                    "Via the Event Loop, Call Stack, and Task/Microtask Queues",
                    "By automatically spawning background OS threads for each function",
                    "Through hardware interrupt registers in the GPU",
                    "By pausing CPU clock cycles until I/O finishes"
                ],
                "correct": "Via the Event Loop, Call Stack, and Task/Microtask Queues",
                "explanation": "JavaScript relies on an event loop model where the call stack executes synchronous code while web APIs schedule callbacks in microtask and macrotask queues.",
                "topic": "Asynchronous JavaScript",
                "difficulty": "intermediate",
                "points": 1.0,
            },
            {
                "question": "What does `Array.prototype.map()` return when executed?",
                "type": "multiple_choice",
                "options": [
                    "A new array with the results of calling the provided function on every element",
                    "The original array mutated in-place",
                    "A boolean indicating if all elements passed the predicate",
                    "A single accumulated scalar value"
                ],
                "correct": "A new array with the results of calling the provided function on every element",
                "explanation": "Array.map is non-mutating and constructs a brand new array containing the transformed items.",
                "topic": "Arrays and Higher Order Functions",
                "difficulty": "intermediate",
                "points": 1.0,
            },
            {
                "question": "What is a closure in JavaScript?",
                "type": "multiple_choice",
                "options": [
                    "A function bundled with references to its surrounding lexical environment",
                    "A method that explicitly terminates browser execution",
                    "An object that has been deeply frozen with Object.freeze()",
                    "A syntax error caused by unclosed curly braces"
                ],
                "correct": "A function bundled with references to its surrounding lexical environment",
                "explanation": "A closure gives an inner function access to its outer function's scope even after the outer function has returned.",
                "topic": "Functions and Closures",
                "difficulty": "intermediate",
                "points": 1.0,
            },
            {
                "question": "What will `[1, 2, 3] + [4, 5, 6]` evaluate to in JavaScript?",
                "type": "multiple_choice",
                "options": ["'1,2,34,5,6'", "[1, 2, 3, 4, 5, 6]", "NaN", "TypeError"],
                "correct": "'1,2,34,5,6'",
                "explanation": "The + operator converts both arrays to strings ('1,2,3' and '4,5,6') and concatenates them.",
                "topic": "Type Coercion",
                "difficulty": "intermediate",
                "points": 1.0,
            },
            {
                "question": "Which Promise method waits for all promises to settle regardless of whether they resolve or reject?",
                "type": "multiple_choice",
                "options": ["Promise.allSettled()", "Promise.all()", "Promise.race()", "Promise.any()"],
                "correct": "Promise.allSettled()",
                "explanation": "Promise.allSettled() returns a promise that fulfills after all of the given promises have either fulfilled or rejected.",
                "topic": "Promises and Async/Await",
                "difficulty": "intermediate",
                "points": 1.0,
            },
            {
                "question": "What will `console.log(this)` output inside an arrow function defined in module scope?",
                "type": "multiple_choice",
                "options": [
                    "The lexical this of the enclosing scope",
                    "The global Window object or undefined in strict mode",
                    "A new empty instance object",
                    "Throws a ReferenceError"
                ],
                "correct": "The lexical this of the enclosing scope",
                "explanation": "Arrow functions do not bind their own this; they retain the this value of the enclosing lexical context.",
                "topic": "Functions and this Binding",
                "difficulty": "advanced",
                "points": 1.0,
            },
        ]
    },
    {
        "skill": "Python",
        "title": "Python Core Architecture & Data Structures",
        "difficulty": "intermediate",
        "time_limit": 25,
        "questions": [
            {
                "question": "Which data structure in Python is mutable, ordered, and allows duplicate elements?",
                "type": "multiple_choice",
                "options": ["list", "tuple", "set", "frozenset"],
                "correct": "list",
                "explanation": "Python lists are mutable, indexed sequences that allow duplicate items.",
                "topic": "Data Structures",
                "difficulty": "beginner",
                "points": 1.0,
            },
            {
                "question": "What is the primary role of the Global Interpreter Lock (GIL) in standard CPython?",
                "type": "multiple_choice",
                "options": [
                    "A mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at once",
                    "A cryptographic cipher that encrypts bytecode files (.pyc)",
                    "A memory compressor that manages garbage collection heaps",
                    "A compiler optimizer that vectorizes loop operations"
                ],
                "correct": "A mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes at once",
                "explanation": "CPython's GIL ensures thread-safe memory management by allowing only one native thread to execute Python bytecode at a time.",
                "topic": "CPython Internals & Concurrency",
                "difficulty": "advanced",
                "points": 1.0,
            },
            {
                "question": "What keyword turns a standard Python function into a generator yielding an iterator?",
                "type": "multiple_choice",
                "options": ["yield", "return", "generate", "async"],
                "correct": "yield",
                "explanation": "Using yield in a function body causes the function to return a generator iterator.",
                "topic": "Generators and Iterators",
                "difficulty": "intermediate",
                "points": 1.0,
            },
            {
                "question": "What is the average time complexity of looking up a key in a standard Python dictionary?",
                "type": "multiple_choice",
                "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
                "correct": "O(1)",
                "explanation": "Python dictionaries are hash tables providing average O(1) constant time lookups.",
                "topic": "Data Structures & Complexity",
                "difficulty": "intermediate",
                "points": 1.0,
            },
        ]
    },
    {
        "skill": "SQL",
        "title": "SQL Relational Queries & Database Design",
        "difficulty": "intermediate",
        "time_limit": 20,
        "questions": [
            {
                "question": "Which JOIN returns all rows from the left table, and matching rows from the right table?",
                "type": "multiple_choice",
                "options": ["LEFT JOIN", "INNER JOIN", "RIGHT JOIN", "FULL OUTER JOIN"],
                "correct": "LEFT JOIN",
                "explanation": "LEFT JOIN returns all records from the left table and matched records from the right table, filling nulls if no match.",
                "topic": "Joins and Aggregations",
                "difficulty": "beginner",
                "points": 1.0,
            },
            {
                "question": "What clause filters aggregated group results produced by a `GROUP BY` statement?",
                "type": "multiple_choice",
                "options": ["HAVING", "WHERE", "ORDER BY", "FILTER"],
                "correct": "HAVING",
                "explanation": "HAVING filters groups created by GROUP BY, whereas WHERE filters individual rows prior to grouping.",
                "topic": "Aggregations and Grouping",
                "difficulty": "intermediate",
                "points": 1.0,
            },
            {
                "question": "What is the primary benefit of creating a B-Tree index on a frequently queried column?",
                "type": "multiple_choice",
                "options": [
                    "Reduces read lookups from O(n) table scans to O(log n) tree traversals",
                    "Reduces disk space by compressing rows",
                    "Automatically encrypts column data",
                    "Prevents any duplicate rows from ever being inserted"
                ],
                "correct": "Reduces read lookups from O(n) table scans to O(log n) tree traversals",
                "explanation": "B-Tree indexes provide efficient logarithmic search times for equality and range queries.",
                "topic": "Indexing & Query Performance",
                "difficulty": "advanced",
                "points": 1.0,
            },
        ]
    },
    {
        "skill": "React",
        "title": "React Component Architecture & Hooks Diagnostic",
        "difficulty": "intermediate",
        "time_limit": 20,
        "questions": [
            {
                "question": "What hook is used in functional React components to trigger side effects such as data fetching or subscriptions?",
                "type": "multiple_choice",
                "options": ["useEffect", "useState", "useMemo", "useContext"],
                "correct": "useEffect",
                "explanation": "useEffect lets you perform side effects in function components.",
                "topic": "React Hooks",
                "difficulty": "beginner",
                "points": 1.0,
            },
            {
                "question": "Why must list items in React have unique and stable `key` props?",
                "type": "multiple_choice",
                "options": [
                    "To help React identify which items have changed, been added, or been removed during reconciliation",
                    "To assign unique CSS IDs for styling",
                    "To enable browser caching in local storage",
                    "To comply with HTML5 validation rules"
                ],
                "correct": "To help React identify which items have changed, been added, or been removed during reconciliation",
                "explanation": "Keys provide identity to virtual DOM nodes so React reorders elements rather than re-rendering everything.",
                "topic": "Reconciliation & Virtual DOM",
                "difficulty": "intermediate",
                "points": 1.0,
            },
        ]
    }
]


async def seed_database():
    print("Initializing database tables...", flush=True)
    await init_db()

    async with AsyncSessionLocal() as session:
        print("Checking existing seed data...", flush=True)

        # 1. Seed Skills
        skill_cache: dict[str, Skill] = {}
        for name, category, desc in SKILLS_DATA:
            res = await session.execute(select(Skill).where(Skill.name == name))
            existing = res.scalar_one_or_none()
            if not existing:
                skill_obj = Skill(
                    id=uuid.uuid4(),
                    name=name,
                    category=category,
                    description=desc,
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(skill_obj)
                skill_cache[name] = skill_obj
            else:
                skill_cache[name] = existing

        await session.flush()
        print(f"Seeded/Verified {len(SKILLS_DATA)} skills.")

        # 2. Seed Career Roles & Requirements
        for cdata in CAREERS_DATA:
            c_res = await session.execute(select(CareerRole).where(CareerRole.slug == cdata["slug"]))
            career_obj = c_res.scalar_one_or_none()
            if not career_obj:
                career_obj = CareerRole(
                    id=uuid.uuid4(),
                    title=cdata["title"],
                    slug=cdata["slug"],
                    category=cdata["category"],
                    demand_level=cdata["demand_level"],
                    avg_salary_range=cdata["avg_salary_range"],
                    description=cdata["description"],
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(career_obj)
                await session.flush()

            # Requirements
            for sname, importance, min_prof, is_crit, rdesc in cdata["requirements"]:
                skill_record = skill_cache.get(sname)
                if skill_record:
                    r_res = await session.execute(
                        select(CareerRequirement).where(
                            CareerRequirement.career_id == career_obj.id,
                            CareerRequirement.skill_id == skill_record.id,
                        )
                    )
                    if not r_res.scalar_one_or_none():
                        req = CareerRequirement(
                            id=uuid.uuid4(),
                            career_id=career_obj.id,
                            skill_id=skill_record.id,
                            importance=importance,
                            min_proficiency=min_prof,
                            is_critical=is_crit,
                            description=rdesc,
                            created_at=datetime.now(timezone.utc),
                        )
                        session.add(req)

        await session.flush()
        print(f"Seeded/Verified {len(CAREERS_DATA)} careers and requirements.")

        # 3. Seed Learning Resources
        resources = [
            ("JavaScript", "Modern JavaScript Tutorial (javascript.info)", "tutorial", "https://javascript.info", "beginner", 20.0, "The Modern JavaScript Tutorial", True),
            ("JavaScript", "MDN JavaScript Guide", "documentation", "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "intermediate", 15.0, "Mozilla Developer Network", True),
            ("JavaScript", "JavaScript: Understanding the Weird Parts", "video", "https://www.youtube.com", "advanced", 12.0, "FreeCodeCamp", True),
            ("React", "Official React Documentation & Interactive Sandbox", "documentation", "https://react.dev", "beginner", 15.0, "React Team", True),
            ("React", "Full Stack Open — Deep Dive Into Modern Web Development", "course", "https://fullstackopen.com/en/", "intermediate", 40.0, "University of Helsinki", True),
            ("Python", "Python 3 Official Documentation & Tutorial", "documentation", "https://docs.python.org/3/tutorial/", "beginner", 15.0, "Python Software Foundation", True),
            ("Python", "Fluent Python: Clear, Concise, and Effective Programming", "article", "https://github.com", "advanced", 30.0, "O'Reilly", False),
            ("SQL", "SQLBolt — Interactive Lessons to Learn SQL", "tutorial", "https://sqlbolt.com", "beginner", 8.0, "SQLBolt", True),
            ("SQL", "PostgreSQL Official Documentation", "documentation", "https://www.postgresql.org/docs/", "intermediate", 25.0, "PostgreSQL Global Development Group", True),
            ("Git", "Pro Git Book (Free Online)", "course", "https://git-scm.com/book/en/v2", "beginner", 10.0, "Scott Chacon & Ben Straub", True),
            ("HTML", "MDN HTML Basics and Semantic Structure", "tutorial", "https://developer.mozilla.org/en-US/docs/Learn/HTML", "beginner", 8.0, "Mozilla", True),
            ("CSS", "CSS-Tricks: Complete Guide to Flexbox & Grid", "article", "https://css-tricks.com/snippets/css/a-guide-to-flexbox/", "intermediate", 6.0, "CSS Tricks", True),
        ]
        for sname, title, rtype, url, diff, hours, prov, is_free in resources:
            sk = skill_cache.get(sname)
            if sk:
                res_check = await session.execute(
                    select(LearningResource).where(LearningResource.title == title)
                )
                if not res_check.scalar_one_or_none():
                    lres = LearningResource(
                        id=uuid.uuid4(),
                        skill_id=sk.id,
                        title=title,
                        resource_type=rtype,
                        url=url,
                        difficulty=diff,
                        estimated_duration_hours=hours,
                        provider=prov,
                        is_free=is_free,
                        description=f"Comprehensive {diff} curriculum covering {sname}.",
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(lres)

        await session.flush()
        print("Seeded learning resources.")

        # 4. Seed Assessments & Questions
        for adata in ASSESSMENTS_DATA:
            sk = skill_cache.get(adata["skill"])
            if not sk:
                continue
            a_res = await session.execute(select(Assessment).where(Assessment.title == adata["title"]))
            assessment_obj = a_res.scalar_one_or_none()
            if not assessment_obj:
                assessment_obj = Assessment(
                    id=uuid.uuid4(),
                    skill_id=sk.id,
                    title=adata["title"],
                    description=f"Standard diagnostic assessment covering {adata['skill']} competencies.",
                    difficulty=adata["difficulty"],
                    time_limit_minutes=adata["time_limit"],
                    passing_score=70.0,
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(assessment_obj)
                await session.flush()

                for idx, qdata in enumerate(adata["questions"]):
                    q_obj = AssessmentQuestion(
                        id=uuid.uuid4(),
                        assessment_id=assessment_obj.id,
                        question_text=qdata["question"],
                        question_type=qdata["type"],
                        options=qdata["options"],
                        correct_answer=qdata["correct"],
                        explanation=qdata["explanation"],
                        topic=qdata["topic"],
                        difficulty=qdata["difficulty"],
                        points=qdata["points"],
                        order_index=idx + 1,
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(q_obj)

        await session.flush()
        print("Seeded assessments and questions.")

        # 5. Seed Demonstration Learner: Alex Morgan
        demo_email = "alex@cognify.ai"
        user_res = await session.execute(select(User).where(User.email == demo_email))
        demo_user = user_res.scalar_one_or_none()

        if not demo_user:
            demo_user = User(
                id=uuid.uuid4(),
                email=demo_email,
                username="alexmorgan",
                password_hash=hash_password("password123"),
                full_name="Alex Morgan",
                role="learner",
                is_active=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(demo_user)
            await session.flush()

            # Target Career: Full Stack Developer
            fs_career = (await session.execute(select(CareerRole).where(CareerRole.slug == "full-stack-developer"))).scalar_one_or_none()

            profile = LearnerProfile(
                id=uuid.uuid4(),
                user_id=demo_user.id,
                target_career_id=fs_career.id if fs_career else None,
                bio="Aspiring Full Stack Engineer transitioning from backend scripting to comprehensive web engineering.",
                education_level="Bachelor's in Computer Science",
                years_experience=1,
                academic_background="Algorithms, Relational Database Systems, Python Automation.",
                certifications=["Python Associate Certified", "SQL Relational Modeling"],
                career_readiness_score=36.5,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            session.add(profile)
            await session.flush()

            # Exact demo skills specified in hackathon requirements:
            # Python: 80%, SQL: 75%, HTML: 40%, CSS: 20%, JavaScript: 0%, React: 0%, Node.js: 0%, Git: 30%
            alex_skills = [
                ("Python", 80.0, "assessed", "assessment"),
                ("SQL", 75.0, "assessed", "assessment"),
                ("HTML", 40.0, "claimed", "self_reported"),
                ("CSS", 20.0, "claimed", "self_reported"),
                ("JavaScript", 0.0, "claimed", "self_reported"),
                ("React", 0.0, "claimed", "self_reported"),
                ("Node.js", 0.0, "claimed", "self_reported"),
                ("Git", 30.0, "claimed", "self_reported"),
            ]

            for sname, prof, conf, src in alex_skills:
                sk = skill_cache.get(sname)
                if sk:
                    ls = LearnerSkill(
                        id=uuid.uuid4(),
                        learner_id=profile.id,
                        skill_id=sk.id,
                        proficiency=prof,
                        confidence=conf,
                        source=src,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    )
                    session.add(ls)

            print("Created Alex Morgan demo learner profile and skills.")

        await session.commit()
        print("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_database())

