import re

from app.models import StudyMaterial, StudyMaterialProgress, User
from extensions import db


def csrf(client, path):
    body = client.get(path).data
    return re.search(rb'name="csrf_token"[^>]+value="([^"]+)"', body).group(1).decode()


def make_material(app):
    with app.app_context():
        material = StudyMaterial(
            subject="Python Programming",
            title="Test variables",
            difficulty="Beginner",
            summary="Learn variables.",
            key_concepts="Names point to values.",
            example="x = 1",
            expected_output="1",
            common_mistakes="Forgetting types.",
            practice_questions="Q: type? A: int.",
            revision_summary="Use clear names.",
        )
        db.session.add(material)
        db.session.commit()
        return material.id


def register_and_login(client):
    client.post("/register", data={"csrf_token": csrf(client, "/register"), "full_name": "Study User", "email": "study@example.com", "password": "secure-pass-123", "confirm_password": "secure-pass-123"})
    return client.post("/login", data={"csrf_token": csrf(client, "/login"), "email": "study@example.com", "password": "secure-pass-123"})


def test_study_materials_search_and_detail(client, app):
    material_id = make_material(app)
    assert client.get("/study-materials").status_code == 200
    assert b"Test variables" in client.get("/study-materials?q=variables").data
    detail = client.get(f"/study-materials/{material_id}")
    assert detail.status_code == 200
    assert b"Expected output" in detail.data


def test_completion_is_user_specific_and_updates_dashboard(client, app):
    material_id = make_material(app)
    register_and_login(client)
    response = client.post(f"/study-materials/{material_id}/complete", data={"csrf_token": csrf(client, f"/study-materials/{material_id}")}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Mark as not completed" in response.data
    with app.app_context():
        user = User.query.filter_by(email="study@example.com").one()
        progress = StudyMaterialProgress.query.filter_by(user_id=user.id, material_id=material_id).one()
        assert progress.completed is True
    assert b"1 topics completed" in client.get("/dashboard").data


def test_pdf_download_and_csrf_protection(client, app):
    material_id = make_material(app)
    pdf = client.get(f"/study-materials/{material_id}/download")
    assert pdf.status_code == 200
    assert pdf.mimetype == "application/pdf"
    assert pdf.data.startswith(b"%PDF")
    register_and_login(client)
    rejected = client.post(f"/study-materials/{material_id}/complete")
    assert rejected.status_code == 400
