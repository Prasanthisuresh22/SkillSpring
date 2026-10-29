from datetime import datetime
from urllib.parse import urlparse

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_
from io import BytesIO
import re
from xml.sax.saxutils import escape
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

from app.main import main
from app.models import (
    Activity, AnswerOption, Challenge, ChallengeProgress, ContactMessage,
    Enrollment, Lesson, LessonProgress, MilestoneProgress, Module, Project,
    ProjectMilestone, Quiz, QuizAttempt, QuizResponse, Resource,
    ResourceBookmark, Roadmap, Skill, StudyMaterial, StudyMaterialProgress, UserProject,
)
from extensions import db


def activity(kind, description):
    db.session.add(Activity(user_id=current_user.id, activity_type=kind, description=description))


def _material_progress_ids():
    if not current_user.is_authenticated:
        return set()
    return {item.material_id for item in StudyMaterialProgress.query.filter_by(user_id=current_user.id, completed=True)}


@main.get("/")
def index():
    featured_paths = [
        {"title": "Python Programming", "description": "Build confidence with syntax, problem solving, and practical automation.", "difficulty": "Beginner", "duration": "6–8 weeks", "icon": "code-2", "accent": "violet"},
        {"title": "Web Development", "description": "Create polished, accessible websites from the ground up.", "difficulty": "Beginner", "duration": "8–10 weeks", "icon": "globe-2", "accent": "blue"},
        {"title": "SQL and Databases", "description": "Learn to model data and write queries that answer real questions.", "difficulty": "Beginner", "duration": "4–6 weeks", "icon": "database", "accent": "green"},
        {"title": "Data Analysis", "description": "Turn messy datasets into useful insights and clear stories.", "difficulty": "Intermediate", "duration": "6–8 weeks", "icon": "bar-chart-3", "accent": "orange"},
        {"title": "AI Fundamentals", "description": "Understand the ideas behind modern AI through approachable practice.", "difficulty": "Intermediate", "duration": "5–7 weeks", "icon": "sparkles", "accent": "pink"},
    ]
    projects = [("Expense Tracker", "Practice data structures and simple reporting.", "Python"), ("Personal Portfolio", "Showcase your skills with an accessible web page.", "HTML / CSS"), ("Library Management System", "Model relationships and manage records with SQL.", "SQL")]
    return render_template("index.html", featured_paths=featured_paths, projects=projects)


@main.get("/dashboard")
@login_required
def dashboard():
    enrollments = Enrollment.query.filter_by(user_id=current_user.id).all()
    completed = LessonProgress.query.filter_by(user_id=current_user.id, completed=True).count()
    total = sum(len(e.roadmap.modules) and sum(len(m.lessons) for m in e.roadmap.modules) for e in enrollments)
    activities = Activity.query.filter_by(user_id=current_user.id).order_by(Activity.created_at.desc()).limit(6).all()
    completed_materials = StudyMaterialProgress.query.filter_by(user_id=current_user.id, completed=True).count()
    recommended = Lesson.query.join(Module).join(Roadmap).filter(
        ~Lesson.id.in_(db.select(LessonProgress.lesson_id).where(LessonProgress.user_id == current_user.id, LessonProgress.completed.is_(True)))
    ).order_by(Roadmap.id, Module.sequence_number, Lesson.sequence_number).first()
    return render_template("dashboard.html", enrollments=enrollments, completed=completed, total=total, activities=activities, recommended=recommended, skills=Skill.query.limit(6).all(), completed_materials=completed_materials)


@main.get("/skills")
def skills():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    statement = Skill.query
    if query:
        statement = statement.filter(or_(Skill.title.ilike(f"%{query}%"), Skill.description.ilike(f"%{query}%")))
    if category:
        statement = statement.filter_by(category=category)
    return render_template("skills.html", skills=statement.order_by(Skill.title).all(), categories=db.session.query(Skill.category).distinct().order_by(Skill.category).all(), query=query, category=category)


@main.get("/skills/<int:skill_id>")
def skill_detail(skill_id):
    skill = db.get_or_404(Skill, skill_id)
    subjects = [skill.title]
    if skill.title == "AI Fundamentals":
        subjects.append("Artificial Intelligence Fundamentals")
    materials = StudyMaterial.query.filter(StudyMaterial.subject.in_(subjects)).order_by(StudyMaterial.sequence_number).all()
    return render_template("skill_detail.html", skill=skill, roadmaps=skill.roadmaps, materials=materials)


@main.post("/roadmaps/<int:roadmap_id>/enroll")
@login_required
def enroll(roadmap_id):
    roadmap = db.get_or_404(Roadmap, roadmap_id)
    if not Enrollment.query.filter_by(user_id=current_user.id, roadmap_id=roadmap.id).first():
        db.session.add(Enrollment(user_id=current_user.id, roadmap_id=roadmap.id))
        activity("enrollment", f"Started {roadmap.title}.")
        db.session.commit()
        flash("You are now enrolled in this roadmap.", "success")
    else:
        flash("You are already enrolled in this roadmap.", "info")
    return redirect(url_for("main.roadmap_detail", roadmap_id=roadmap.id))


@main.get("/roadmaps")
def roadmaps():
    return render_template("roadmaps.html", roadmaps=Roadmap.query.order_by(Roadmap.title).all())


@main.get("/roadmaps/<int:roadmap_id>")
def roadmap_detail(roadmap_id):
    roadmap = db.get_or_404(Roadmap, roadmap_id)
    enrolled = current_user.is_authenticated and Enrollment.query.filter_by(user_id=current_user.id, roadmap_id=roadmap.id).first() is not None
    completed_ids = set()
    if current_user.is_authenticated:
        completed_ids = {p.lesson_id for p in LessonProgress.query.filter_by(user_id=current_user.id, completed=True).all()}
    lessons = [lesson for module in roadmap.modules for lesson in module.lessons]
    return render_template("roadmap_detail.html", roadmap=roadmap, enrolled=enrolled, completed_ids=completed_ids, lesson_count=len(lessons))


@main.post("/lessons/<int:lesson_id>/complete")
@login_required
def complete_lesson(lesson_id):
    lesson = db.get_or_404(Lesson, lesson_id)
    progress = LessonProgress.query.filter_by(user_id=current_user.id, lesson_id=lesson.id).first()
    if progress is None:
        progress = LessonProgress(user_id=current_user.id, lesson_id=lesson.id)
        db.session.add(progress)
    progress.completed = True
    progress.completed_at = datetime.utcnow()
    activity("lesson", f"Completed {lesson.title}.")
    db.session.commit()
    flash("Lesson marked complete.", "success")
    return redirect(request.referrer or url_for("main.roadmap_detail", roadmap_id=lesson.module.roadmap_id))


@main.get("/projects")
def projects():
    return render_template("projects.html", projects=Project.query.order_by(Project.title).all())


@main.get("/projects/<int:project_id>")
def project_detail(project_id):
    project = db.get_or_404(Project, project_id)
    started = current_user.is_authenticated and UserProject.query.filter_by(user_id=current_user.id, project_id=project.id).first()
    done = set()
    if current_user.is_authenticated:
        done = {p.milestone_id for p in MilestoneProgress.query.filter_by(user_id=current_user.id, completed=True).join(ProjectMilestone).filter(ProjectMilestone.project_id == project.id)}
    return render_template("project_detail.html", project=project, started=started, done=done)


@main.post("/projects/<int:project_id>/start")
@login_required
def start_project(project_id):
    project = db.get_or_404(Project, project_id)
    if not UserProject.query.filter_by(user_id=current_user.id, project_id=project.id).first():
        db.session.add(UserProject(user_id=current_user.id, project_id=project.id))
        activity("project", f"Started {project.title}.")
        db.session.commit()
    flash("Project added to your workspace.", "success")
    return redirect(url_for("main.project_detail", project_id=project.id))


@main.post("/milestones/<int:milestone_id>/complete")
@login_required
def complete_milestone(milestone_id):
    milestone = db.get_or_404(ProjectMilestone, milestone_id)
    if not UserProject.query.filter_by(user_id=current_user.id, project_id=milestone.project_id).first():
        abort(403)
    progress = MilestoneProgress.query.filter_by(user_id=current_user.id, milestone_id=milestone.id).first()
    if progress is None:
        progress = MilestoneProgress(user_id=current_user.id, milestone_id=milestone.id)
        db.session.add(progress)
    progress.completed = not progress.completed
    progress.completed_at = datetime.utcnow() if progress.completed else None
    db.session.commit()
    return redirect(url_for("main.project_detail", project_id=milestone.project_id))


@main.get("/challenges")
def challenges():
    completed = {p.challenge_id for p in ChallengeProgress.query.filter_by(user_id=current_user.id, status="completed")} if current_user.is_authenticated else set()
    return render_template("challenges.html", challenges=Challenge.query.order_by(Challenge.category, Challenge.title).all(), completed=completed)


@main.post("/challenges/<int:challenge_id>/complete")
@login_required
def complete_challenge(challenge_id):
    challenge = db.get_or_404(Challenge, challenge_id)
    if not ChallengeProgress.query.filter_by(user_id=current_user.id, challenge_id=challenge.id).first():
        db.session.add(ChallengeProgress(user_id=current_user.id, challenge_id=challenge.id))
        activity("challenge", f"Completed {challenge.title}.")
        db.session.commit()
    flash("Challenge completed.", "success")
    return redirect(url_for("main.challenges"))


@main.get("/quizzes")
def quizzes():
    return render_template("quizzes.html", quizzes=Quiz.query.order_by(Quiz.title).all())


@main.route("/quizzes/<int:quiz_id>", methods=["GET", "POST"])
@login_required
def quiz_detail(quiz_id):
    quiz = db.get_or_404(Quiz, quiz_id)
    if request.method == "POST":
        attempt = QuizAttempt(user_id=current_user.id, quiz_id=quiz.id, score=0, total_questions=len(quiz.questions))
        db.session.add(attempt)
        score = 0
        for question in quiz.questions:
            selected = request.form.get(f"question_{question.id}")
            option = db.session.get(AnswerOption, int(selected)) if selected and selected.isdigit() else None
            correct = bool(option and option.question_id == question.id and option.is_correct)
            score += correct
            attempt.responses.append(QuizResponse(question_id=question.id, selected_option_id=option.id if option else None, is_correct=correct))
        attempt.score = score
        db.session.commit()
        flash(f"Quiz submitted: {score}/{attempt.total_questions}.", "success")
        return redirect(url_for("main.quiz_result", attempt_id=attempt.id))
    return render_template("quiz_detail.html", quiz=quiz)


@main.get("/quizzes/results/<int:attempt_id>")
@login_required
def quiz_result(attempt_id):
    attempt = db.get_or_404(QuizAttempt, attempt_id)
    if attempt.user_id != current_user.id:
        abort(403)
    return render_template("quiz_result.html", attempt=attempt)


@main.get("/resources")
def resources():
    query = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()
    statement = Resource.query
    if query:
        statement = statement.filter(or_(Resource.title.ilike(f"%{query}%"), Resource.description.ilike(f"%{query}%")))
    if category:
        statement = statement.filter_by(category=category)
    bookmarks = {b.resource_id for b in ResourceBookmark.query.filter_by(user_id=current_user.id)} if current_user.is_authenticated else set()
    return render_template("resources.html", resources=statement.order_by(Resource.title).all(), categories=db.session.query(Resource.category).distinct().order_by(Resource.category).all(), query=query, category=category, bookmarks=bookmarks)


@main.post("/resources/<int:resource_id>/bookmark")
@login_required
def bookmark_resource(resource_id):
    resource = db.get_or_404(Resource, resource_id)
    bookmark = ResourceBookmark.query.filter_by(user_id=current_user.id, resource_id=resource.id).first()
    if bookmark:
        db.session.delete(bookmark)
    else:
        db.session.add(ResourceBookmark(user_id=current_user.id, resource_id=resource.id))
    db.session.commit()
    return redirect(request.referrer or url_for("main.resources"))


@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        name = " ".join(request.form.get("full_name", "").strip().split())
        goal = request.form.get("learning_goal", "").strip()
        if len(name) < 2:
            flash("Please enter a valid name.", "error")
        else:
            current_user.full_name, current_user.learning_goal = name, goal[:255]
            db.session.commit()
            flash("Profile updated.", "success")
            return redirect(url_for("main.profile"))
    return render_template("profile.html")


@main.get("/progress")
@login_required
def progress():
    lessons = LessonProgress.query.filter_by(user_id=current_user.id, completed=True).count()
    attempts = QuizAttempt.query.filter_by(user_id=current_user.id).order_by(QuizAttempt.submitted_at.desc()).all()
    milestones = MilestoneProgress.query.filter_by(user_id=current_user.id, completed=True).count()
    return render_template("progress.html", lessons=lessons, attempts=attempts, milestones=milestones)


@main.get("/study-materials")
def study_materials():
    query = request.args.get("q", "").strip()
    subject = request.args.get("subject", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    statement = StudyMaterial.query
    if query:
        statement = statement.filter(or_(StudyMaterial.title.ilike(f"%{query}%"), StudyMaterial.summary.ilike(f"%{query}%"), StudyMaterial.key_concepts.ilike(f"%{query}%")))
    if subject:
        statement = statement.filter_by(subject=subject)
    if difficulty:
        statement = statement.filter_by(difficulty=difficulty)
    materials = statement.order_by(StudyMaterial.subject, StudyMaterial.sequence_number).all()
    return render_template("study_materials.html", materials=materials, subjects=db.session.query(StudyMaterial.subject).distinct().order_by(StudyMaterial.subject).all(), query=query, subject=subject, difficulty=difficulty, completed_ids=_material_progress_ids())


@main.get("/study-materials/<int:material_id>")
def study_material_detail(material_id):
    material = db.get_or_404(StudyMaterial, material_id)
    completed = material.id in _material_progress_ids()
    siblings = StudyMaterial.query.filter_by(subject=material.subject).order_by(StudyMaterial.sequence_number).all()
    index = next((i for i, item in enumerate(siblings) if item.id == material.id), 0)
    return render_template("study_material_detail.html", material=material, completed=completed, previous=siblings[index - 1] if index else None, next_material=siblings[index + 1] if index + 1 < len(siblings) else None)


@main.post("/study-materials/<int:material_id>/complete")
@login_required
def complete_study_material(material_id):
    material = db.get_or_404(StudyMaterial, material_id)
    progress = StudyMaterialProgress.query.filter_by(user_id=current_user.id, material_id=material.id).first()
    if progress is None:
        progress = StudyMaterialProgress(user_id=current_user.id, material_id=material.id)
        db.session.add(progress)
    progress.completed = not progress.completed
    progress.completed_at = datetime.utcnow() if progress.completed else None
    activity("study-material", f"{'Completed' if progress.completed else 'Reopened'} {material.title}.")
    db.session.commit()
    flash("Study material progress updated.", "success")
    return redirect(request.referrer or url_for("main.study_material_detail", material_id=material.id))


@main.get("/study-materials/<int:material_id>/download")
def download_study_material(material_id):
    material = db.get_or_404(StudyMaterial, material_id)
    buffer = BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=letter, title=material.title)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"SkillSpring Study Notes: {material.title}", styles["Title"]), Paragraph(f"Subject: {material.subject} | Difficulty: {material.difficulty}", styles["Normal"]), Spacer(1, 12)]
    sections = [("Overview", material.summary), ("Key concepts", material.key_concepts), ("Example", material.example), ("Expected output", material.expected_output), ("Common mistakes and tips", material.common_mistakes), ("Practice questions and answers", material.practice_questions), ("Revision summary", material.revision_summary)]
    for heading, content in sections:
        story.extend([Paragraph(heading, styles["Heading2"]), Paragraph(escape(content).replace("\n", "<br/>"), styles["BodyText"]), Spacer(1, 10)])
    document.build(story)
    buffer.seek(0)
    filename = re.sub(r"[^a-z0-9]+", "-", material.title.lower()).strip("-") + ".pdf"
    from flask import send_file
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype="application/pdf")


@main.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name, email, message = request.form.get("name", "").strip(), request.form.get("email", "").strip().lower(), request.form.get("message", "").strip()
        if len(name) < 2 or "@" not in email or len(message) < 10:
            flash("Please provide a valid name, email, and message of at least 10 characters.", "error")
        else:
            db.session.add(ContactMessage(name=name, email=email, message=message))
            db.session.commit()
            flash("Your message has been submitted. Email delivery is not configured.", "success")
            return redirect(url_for("main.contact"))
    return render_template("contact.html")


@main.get("/about")
def about():
    return render_template("info.html", page_title="About SkillSpring", heading="Learning that moves with you.", body="SkillSpring helps students turn curiosity into consistent practice and practical proof of their skills.")


@main.get("/privacy")
def privacy():
    return render_template("info.html", page_title="Privacy Policy", heading="Your learning data stays yours.", body="SkillSpring stores account details and learning activity in its SQLite database to provide the features you use. We do not sell personal information.")


@main.get("/terms")
def terms():
    return render_template("info.html", page_title="Terms of Use", heading="Use SkillSpring to learn and build.", body="Use the platform responsibly and do not submit private, unlawful, or harmful content. Learning resources link to their original publishers.")
