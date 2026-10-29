def test_application_starts(app):
    assert app is not None
    assert app.config["TESTING"] is True


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "service": "skillspring"}


def test_custom_not_found_page(client):
    response = client.get("/does-not-exist")
    assert response.status_code == 404
    assert b"Page not found" in response.data


def test_landing_page_content(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"SkillSpring" in response.data
    assert b"Your next skill" in response.data
    assert b"Start learning" in response.data


def test_static_assets_load(client):
    assert client.get("/static/css/style.css").status_code == 200
    assert client.get("/static/js/main.js").status_code == 200


def test_internal_links_render_without_build_errors(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"href=\"/\"" in response.data
    assert b"href=\"/auth/login\"" in response.data
