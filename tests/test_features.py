import re

from app.models import AnswerOption, Lesson, Module, Project, ProjectMilestone, Question, Quiz, Roadmap, Skill
from extensions import db


def token(client, path="/register"):
    body = client.get(path).data
    return re.search(rb'name="csrf_token"[^>]+value="([^"]+)"', body).group(1).decode()


def logged_in_client(client, app):
    with app.app_context():
        skill = Skill(title="Python", description="Learn Python.", category="Programming", difficulty="Beginner", estimated_hours=10)
        db.session.add(skill)
        roadmap = Roadmap(title="Python Roadmap", description="Learn Python.", difficulty="Beginner", estimated_hours=10, skill=skill)
        db.session.add(roadmap)
        module = Module(title="Basics", description="Basics", sequence_number=1, roadmap=roadmap)
        db.session.add(module)
        lesson = Lesson(title="Variables", description="Variables", content="Practice", sequence_number=1, module=module)
        db.session.add(lesson)
        project = Project(title="Portfolio", description="Build it.", difficulty="Beginner", technology_stack="HTML", instructions="Build it.")
        db.session.add(project)
        db.session.flush()
        db.session.add(ProjectMilestone(title="First section", sequence_number=1, project=project))
        quiz = Quiz(title="Python quiz", description="Basics", category="Python")
        db.session.add(quiz)
        db.session.flush()
        question = Question(quiz_id=quiz.id, question_text="Two plus two?", explanation="It is four.", sequence_number=1)
        db.session.add(question)
        db.session.flush()
        db.session.add(AnswerOption(question_id=question.id, option_text="4", is_correct=True))
        db.session.commit()
        ids = roadmap.id, lesson.id, project.id, quiz.id
    client.post("/register", data={"csrf_token": token(client), "full_name": "Feature User", "email": "feature@example.com", "password": "secure-pass-123", "confirm_password": "secure-pass-123"})
    client.post("/login", data={"csrf_token": token(client, "/login"), "email": "feature@example.com", "password": "secure-pass-123"})
    return ids


def test_catalog_search_and_enrollment(client, app):
    roadmap_id, lesson_id, _, _ = logged_in_client(client, app)
    assert client.get("/skills?q=Python").status_code == 200
    assert client.post(f"/roadmaps/{roadmap_id}/enroll", data={"csrf_token": token(client, f"/roadmaps/{roadmap_id}")}).status_code == 302
    client.post(f"/roadmaps/{roadmap_id}/enroll", data={"csrf_token": token(client, f"/roadmaps/{roadmap_id}")})
    assert client.post(f"/lessons/{lesson_id}/complete", data={"csrf_token": token(client, "/dashboard")}).status_code == 302


def test_project_quiz_profile_and_contact(client, app):
    _, _, project_id, quiz_id = logged_in_client(client, app)
    assert client.post(f"/projects/{project_id}/start", data={"csrf_token": token(client, f"/projects/{project_id}")}).status_code == 302
    with app.app_context():
        option = AnswerOption.query.first()
        question = Question.query.first()
    result = client.post(f"/quizzes/{quiz_id}", data={"csrf_token": token(client, f"/quizzes/{quiz_id}"), f"question_{question.id}": str(option.id)}, follow_redirects=True)
    assert b"1 / 1" in result.data
    profile = client.post("/profile", data={"csrf_token": token(client, "/profile"), "full_name": "Updated User", "learning_goal": "Build projects"}, follow_redirects=True)
    assert b"Profile updated" in profile.data
    contact = client.post("/contact", data={"csrf_token": token(client, "/contact"), "name": "Visitor", "email": "visitor@example.com", "message": "A useful message here."}, follow_redirects=True)
    assert b"message has been submitted" in contact.data
