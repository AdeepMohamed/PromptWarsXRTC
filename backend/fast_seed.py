"""
Fast, optimized seed script for COGNIFY AI targeting Neon PostgreSQL.
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

from seed_data import SKILLS_DATA, CAREERS_DATA, ASSESSMENTS_DATA


async def fast_seed():
    print("Connecting to Neon PostgreSQL...", flush=True)

    async with AsyncSessionLocal() as session:
        print("Checking existing records in Neon...", flush=True)

        # 1. Load existing skills in 1 round trip
        existing_skills_res = await session.execute(select(Skill))
        skill_cache: dict[str, Skill] = {s.name: s for s in existing_skills_res.scalars().all()}

        new_skills = []
        for name, category, desc in SKILLS_DATA:
            if name not in skill_cache:
                s_obj = Skill(
                    id=uuid.uuid4(),
                    name=name,
                    category=category,
                    description=desc,
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(s_obj)
                skill_cache[name] = s_obj
                new_skills.append(s_obj)

        if new_skills:
            await session.commit()
            print(f"Inserted {len(new_skills)} skills into Neon.", flush=True)
        else:
            print(f"Skills already present in Neon ({len(skill_cache)} skills).", flush=True)

        # 2. Careers & Requirements in 1 round trip
        existing_careers = {c.slug: c for c in (await session.execute(select(CareerRole))).scalars().all()}
        existing_reqs = set((r.career_id, r.skill_id) for r in (await session.execute(select(CareerRequirement))).scalars().all())

        for cdata in CAREERS_DATA:
            slug = cdata["slug"]
            if slug not in existing_careers:
                c_obj = CareerRole(
                    id=uuid.uuid4(),
                    title=cdata["title"],
                    slug=slug,
                    category=cdata["category"],
                    demand_level=cdata["demand_level"],
                    avg_salary_range=cdata["avg_salary_range"],
                    description=cdata["description"],
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(c_obj)
                existing_careers[slug] = c_obj
                await session.flush()
            else:
                c_obj = existing_careers[slug]

            # Requirements
            for sname, importance, min_prof, is_crit, rdesc in cdata["requirements"]:
                sk = skill_cache.get(sname)
                if sk and (c_obj.id, sk.id) not in existing_reqs:
                    req = CareerRequirement(
                        id=uuid.uuid4(),
                        career_id=c_obj.id,
                        skill_id=sk.id,
                        importance=importance,
                        min_proficiency=min_prof,
                        is_critical=is_crit,
                        description=rdesc,
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(req)
                    existing_reqs.add((c_obj.id, sk.id))

        await session.commit()
        print("Careers & Requirements synchronized with Neon.", flush=True)

        # 3. Learning Resources
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
        existing_res_titles = set(r.title for r in (await session.execute(select(LearningResource))).scalars().all())
        for sname, title, rtype, url, diff, hours, prov, is_free in resources:
            if title not in existing_res_titles:
                sk = skill_cache.get(sname)
                if sk:
                    session.add(LearningResource(
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
                    ))
                    existing_res_titles.add(title)

        await session.commit()
        print("Learning Resources synchronized with Neon.", flush=True)

        # 4. Assessments & Questions
        existing_assessments = {a.title: a for a in (await session.execute(select(Assessment))).scalars().all()}
        for adata in ASSESSMENTS_DATA:
            title = adata["title"]
            sk = skill_cache.get(adata["skill"])
            if not sk:
                continue

            if title not in existing_assessments:
                a_obj = Assessment(
                    id=uuid.uuid4(),
                    skill_id=sk.id,
                    title=title,
                    description=f"Diagnostic assessment covering {adata['skill']} competencies.",
                    difficulty=adata["difficulty"],
                    time_limit_minutes=adata["time_limit"],
                    passing_score=70.0,
                    is_active=True,
                    created_at=datetime.now(timezone.utc),
                )
                session.add(a_obj)
                await session.flush()
                existing_assessments[title] = a_obj

                for idx, qdata in enumerate(adata["questions"]):
                    session.add(AssessmentQuestion(
                        id=uuid.uuid4(),
                        assessment_id=a_obj.id,
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
                    ))

        await session.commit()
        print("Assessments & Questions synchronized with Neon.", flush=True)

        # 5. Seed Alex Morgan
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

            fs_career = existing_careers.get("full-stack-developer")
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
                    session.add(LearnerSkill(
                        id=uuid.uuid4(),
                        learner_id=profile.id,
                        skill_id=sk.id,
                        proficiency=prof,
                        confidence=conf,
                        source=src,
                        created_at=datetime.now(timezone.utc),
                        updated_at=datetime.now(timezone.utc),
                    ))

            await session.commit()
            print("Alex Morgan demo learner created in Neon PostgreSQL.", flush=True)

        print("SUCCESS: Neon PostgreSQL database completely populated!", flush=True)


if __name__ == "__main__":
    asyncio.run(fast_seed())
