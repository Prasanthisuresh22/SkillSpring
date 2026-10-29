from datetime import datetime, timezone

from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    preferred_interests = db.Column(db.String(500))
    learning_goal = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    enrollments = db.relationship("Enrollment", back_populates="user", cascade="all, delete-orphan")
    lesson_progress = db.relationship("LessonProgress", back_populates="user", cascade="all, delete-orphan")
    challenge_progress = db.relationship("ChallengeProgress", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = db.relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    projects = db.relationship("UserProject", back_populates="user", cascade="all, delete-orphan")
    activities = db.relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    resource_bookmarks = db.relationship("ResourceBookmark", back_populates="user", cascade="all, delete-orphan")
    study_material_progress = db.relationship("StudyMaterialProgress", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False, index=True)
    difficulty = db.Column(db.String(30), nullable=False)
    estimated_hours = db.Column(db.Integer, nullable=False, default=1)
    roadmaps = db.relationship("Roadmap", back_populates="skill")


class Roadmap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(30), nullable=False)
    estimated_hours = db.Column(db.Integer, nullable=False, default=1)
    skill_id = db.Column(db.Integer, db.ForeignKey("skill.id"))
    skill = db.relationship("Skill", back_populates="roadmaps")
    modules = db.relationship("Module", back_populates="roadmap", cascade="all, delete-orphan", order_by="Module.sequence_number")
    enrollments = db.relationship("Enrollment", back_populates="roadmap", cascade="all, delete-orphan")


class Module(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmap.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)
    roadmap = db.relationship("Roadmap", back_populates="modules")
    lessons = db.relationship("Lesson", back_populates="module", cascade="all, delete-orphan", order_by="Lesson.sequence_number")


class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    module_id = db.Column(db.Integer, db.ForeignKey("module.id"), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)
    estimated_minutes = db.Column(db.Integer, nullable=False, default=30)
    module = db.relationship("Module", back_populates="lessons")


class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    roadmap_id = db.Column(db.Integer, db.ForeignKey("roadmap.id"), nullable=False)
    enrolled_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    user = db.relationship("User", back_populates="enrollments")
    roadmap = db.relationship("Roadmap", back_populates="enrollments")
    __table_args__ = (db.UniqueConstraint("user_id", "roadmap_id", name="uq_enrollment_user_roadmap"),)


class LessonProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lesson.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime(timezone=True))
    user = db.relationship("User", back_populates="lesson_progress")
    lesson = db.relationship("Lesson")
    __table_args__ = (db.UniqueConstraint("user_id", "lesson_id", name="uq_lesson_progress_user_lesson"),)


class Challenge(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    difficulty = db.Column(db.String(30), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text)
    hints = db.Column(db.Text)


class ChallengeProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey("challenge.id"), nullable=False)
    status = db.Column(db.String(30), default="completed", nullable=False)
    completed_at = db.Column(db.DateTime(timezone=True), default=utcnow)
    user = db.relationship("User", back_populates="challenge_progress")
    challenge = db.relationship("Challenge")
    __table_args__ = (db.UniqueConstraint("user_id", "challenge_id", name="uq_challenge_progress_user_challenge"),)


class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    questions = db.relationship("Question", back_populates="quiz", cascade="all, delete-orphan", order_by="Question.sequence_number")


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)
    quiz = db.relationship("Quiz", back_populates="questions")
    options = db.relationship("AnswerOption", back_populates="question", cascade="all, delete-orphan")


class AnswerOption(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    option_text = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, default=False, nullable=False)
    question = db.relationship("Question", back_populates="options")


class QuizAttempt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    submitted_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    user = db.relationship("User", back_populates="quiz_attempts")
    quiz = db.relationship("Quiz")
    responses = db.relationship("QuizResponse", back_populates="attempt", cascade="all, delete-orphan")


class QuizResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempt.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"), nullable=False)
    selected_option_id = db.Column(db.Integer, db.ForeignKey("answer_option.id"))
    is_correct = db.Column(db.Boolean, nullable=False)
    attempt = db.relationship("QuizAttempt", back_populates="responses")
    question = db.relationship("Question")


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(30), nullable=False)
    technology_stack = db.Column(db.String(255), nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    milestones = db.relationship("ProjectMilestone", back_populates="project", cascade="all, delete-orphan", order_by="ProjectMilestone.sequence_number")


class UserProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    status = db.Column(db.String(30), default="saved", nullable=False)
    saved_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    completed_at = db.Column(db.DateTime(timezone=True))
    user = db.relationship("User", back_populates="projects")
    project = db.relationship("Project")
    __table_args__ = (db.UniqueConstraint("user_id", "project_id", name="uq_user_project"),)


class ProjectMilestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("project.id"), nullable=False)
    title = db.Column(db.String(160), nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False)
    project = db.relationship("Project", back_populates="milestones")


class MilestoneProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    milestone_id = db.Column(db.Integer, db.ForeignKey("project_milestone.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime(timezone=True))
    __table_args__ = (db.UniqueConstraint("user_id", "milestone_id", name="uq_milestone_progress_user_milestone"),)


class Resource(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(160), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(80), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    source_name = db.Column(db.String(120), nullable=False)


class ResourceBookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    user = db.relationship("User", back_populates="resource_bookmarks")
    resource = db.relationship("Resource")
    __table_args__ = (db.UniqueConstraint("user_id", "resource_id", name="uq_resource_bookmark"),)


class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    activity_type = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    user = db.relationship("User", back_populates="activities")


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)


class StudyMaterial(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False, index=True)
    title = db.Column(db.String(180), nullable=False)
    difficulty = db.Column(db.String(30), nullable=False, default="Beginner")
    summary = db.Column(db.Text, nullable=False)
    key_concepts = db.Column(db.Text, nullable=False)
    example = db.Column(db.Text, nullable=False)
    expected_output = db.Column(db.Text, nullable=False)
    common_mistakes = db.Column(db.Text, nullable=False)
    practice_questions = db.Column(db.Text, nullable=False)
    revision_summary = db.Column(db.Text, nullable=False)
    sequence_number = db.Column(db.Integer, nullable=False, default=1)
    progress = db.relationship("StudyMaterialProgress", back_populates="material", cascade="all, delete-orphan")
    __table_args__ = (db.UniqueConstraint("subject", "title", name="uq_study_material_subject_title"),)


class StudyMaterialProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey("study_material.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime(timezone=True))
    user = db.relationship("User", back_populates="study_material_progress")
    material = db.relationship("StudyMaterial", back_populates="progress")
    __table_args__ = (db.UniqueConstraint("user_id", "material_id", name="uq_study_progress_user_material"),)
