import math

import pytest

from app import (
    PROGRAMS,
    build_weekly_schedule,
    calculate_bmi,
    calculate_target_calories,
    create_app,
    suggest_program,
)


def test_health_check():
    app = create_app()
    client = app.test_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_calculate_bmi():
    bmi = calculate_bmi(175, 70)
    assert math.isclose(bmi, 22.86, rel_tol=1e-2)


@pytest.mark.parametrize(
    ("height", "weight"),
    [(0, 70), (175, 0), (-175, 70), (175, float("inf")), (float("nan"), 70)],
)
def test_calculate_bmi_rejects_invalid_measurements(height, weight):
    with pytest.raises(ValueError):
        calculate_bmi(height, weight)


def test_target_calories_for_fat_loss():
    calories = calculate_target_calories(70, "fat loss")
    assert calories == 1850


def test_target_calories_rejects_invalid_weight():
    with pytest.raises(ValueError):
        calculate_target_calories(0, "fat loss")


def test_suggest_program_for_goals():
    fat_loss_plan = suggest_program("fat loss")
    assert fat_loss_plan["name"] == "Fat Loss (FL)"

    muscle_gain_plan = suggest_program("muscle gain")
    assert muscle_gain_plan["name"] == "Muscle Gain (MG)"

    performance_plan = suggest_program("performance training")
    assert performance_plan["name"] == "Performance (PR)"


def test_weekly_schedule_contains_program_workout_and_nutrition():
    schedule = build_weekly_schedule("Beginner (BG)")
    assert schedule["program"] == "Beginner (BG)"
    assert schedule["days"] == suggest_program("beginner")["workout"]
    assert schedule["nutrition"] == suggest_program("beginner")["diet"]


def test_program_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/plan?goal=fat%20loss&height=175&weight=70&age=28")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["goal"] == "fat loss"
    assert payload["program"]["name"] == "Fat Loss (FL)"
    assert payload["bmi_category"] == "Normal"
    assert "weekly_schedule" in payload


@pytest.mark.parametrize(
    "query",
    [
        "?height=invalid",
        "?weight=invalid",
        "?age=invalid",
        "?height=0",
        "?weight=0",
        "?age=0",
        "?height=inf",
    ],
)
def test_plan_endpoint_rejects_invalid_query_values(query):
    client = create_app().test_client()
    response = client.get(f"/api/plan{query}")
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_summary_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/summary?goal=muscle%20gain&height=180&weight=80")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["recommended_plan"]["name"] == "Muscle Gain (MG)"
    assert payload["target_calories"] > 0


def test_programs_endpoint_lists_all_programs():
    client = create_app().test_client()
    response = client.get("/api/programs")
    assert response.status_code == 200
    assert len(response.get_json()["programs"]) == 4


def test_programs_include_detailed_meals_and_exercises():
    client = create_app().test_client()
    response = client.get("/api/programs")
    programs = response.get_json()["programs"]
    assert all(len(program["meals"]) >= 4 for program in programs)
    assert all(len(program["exercises"]) >= 3 for program in programs)
    assert all("protein_g" in meal for program in programs for meal in program["meals"])


def test_program_plans_include_rich_exercise_and_meal_details():
    response = create_app().test_client().get("/api/plan")
    payload = response.get_json()
    assert len(payload["weekly_schedule"]["exercises"]) >= 3
    assert len(payload["weekly_schedule"]["meals"]) >= 4
    assert all("sets" in exercise for exercise in payload["weekly_schedule"]["exercises"])


@pytest.fixture
def api_client(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "fitness-test.db")})
    return app.test_client()


def create_client(api_client, **overrides):
    payload = {
        "name": "Asha Kumar",
        "age": 29,
        "height_cm": 168,
        "weight_kg": 64,
        "goal": "fat loss",
        "experience": "intermediate",
    }
    payload.update(overrides)
    response = api_client.post("/api/clients", json=payload)
    return response


def test_client_profiles_can_be_created_listed_and_updated(api_client):
    created = create_client(api_client)
    assert created.status_code == 201
    profile = created.get_json()["client"]
    client_id = profile["id"]
    assert profile["bmi"] == calculate_bmi(168, 64)
    assert profile["target_calories"] == calculate_target_calories(64, "fat loss")

    listed = api_client.get("/api/clients").get_json()["clients"]
    assert len(listed) == 1
    assert listed[0]["name"] == "Asha Kumar"

    updated = api_client.put(
        f"/api/clients/{client_id}",
        json={
            "name": "Asha Kumar",
            "age": 30,
            "height_cm": 168,
            "weight_kg": 62,
            "goal": "muscle gain",
        },
    )
    assert updated.status_code == 200
    assert updated.get_json()["client"]["age"] == 30
    assert updated.get_json()["client"]["weight_kg"] == 62


def test_duplicate_client_and_invalid_client_inputs_are_rejected(api_client):
    assert create_client(api_client).status_code == 201
    duplicate = create_client(api_client, name="asha kumar")
    assert duplicate.status_code == 409
    invalid = create_client(api_client, age=0)
    assert invalid.status_code == 400
    assert "error" in invalid.get_json()
    wrong_content_type = api_client.post("/api/clients", data="not-json")
    assert wrong_content_type.status_code == 400


def test_client_profiles_persist_across_app_instances(api_client):
    created = create_client(api_client)
    assert created.status_code == 201
    database = api_client.application.config["DATABASE"]

    restarted_client = create_app(
        {"TESTING": True, "DATABASE": database}
    ).test_client()
    persisted = restarted_client.get("/api/clients").get_json()["clients"]
    assert len(persisted) == 1
    assert persisted[0]["name"] == "Asha Kumar"


def test_workouts_and_progress_are_saved_and_listed(api_client):
    client_id = create_client(api_client).get_json()["client"]["id"]

    workout = api_client.post(
        f"/api/clients/{client_id}/workouts",
        json={
            "workout_type": "Full body strength",
            "duration_min": 45,
            "workout_date": "2026-10-10",
            "notes": "Felt strong",
        },
    )
    assert workout.status_code == 201
    assert workout.get_json()["workout"]["duration_min"] == 45
    assert len(api_client.get(f"/api/clients/{client_id}/workouts").get_json()["workouts"]) == 1

    progress = api_client.post(
        f"/api/clients/{client_id}/progress",
        json={"weight_kg": 63.5, "adherence_pct": 80, "notes": "Good week"},
    )
    assert progress.status_code == 201
    assert progress.get_json()["progress"]["adherence_pct"] == 80
    assert len(api_client.get(f"/api/clients/{client_id}/progress").get_json()["progress"]) == 1


@pytest.mark.parametrize(
    ("endpoint", "payload"),
    [
        ("workouts", {"workout_type": "Run", "duration_min": 0}),
        ("workouts", {"workout_type": "Run", "duration_min": 30, "workout_date": "yesterday"}),
        ("progress", {"weight_kg": 0, "adherence_pct": 50}),
        ("progress", {"weight_kg": 60, "adherence_pct": 101}),
    ],
)
def test_invalid_workout_and_progress_records_return_bad_request(
    api_client, endpoint, payload
):
    client_id = create_client(api_client).get_json()["client"]["id"]
    response = api_client.post(f"/api/clients/{client_id}/{endpoint}", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_deleting_client_cascades_to_workouts_and_progress(api_client):
    client_id = create_client(api_client).get_json()["client"]["id"]
    api_client.post(
        f"/api/clients/{client_id}/workouts",
        json={"workout_type": "Walk", "duration_min": 30},
    )
    api_client.post(
        f"/api/clients/{client_id}/progress",
        json={"weight_kg": 63, "adherence_pct": 70},
    )
    deleted = api_client.delete(f"/api/clients/{client_id}")
    assert deleted.status_code == 204
    assert api_client.get(f"/api/clients/{client_id}").status_code == 404
    assert api_client.get(f"/api/clients/{client_id}/workouts").status_code == 404


def test_version_feature_flags_expose_only_the_features_for_that_milestone(tmp_path):
    catalog_app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "catalog.db"),
            "ENABLE_CLIENTS": False,
            "ENABLE_ACTIVITY_TRACKING": False,
        }
    )
    client_app = create_app(
        {
            "TESTING": True,
            "DATABASE": str(tmp_path / "clients.db"),
            "ENABLE_ACTIVITY_TRACKING": False,
        }
    )
    assert catalog_app.test_client().get("/api/programs").status_code == 200
    assert catalog_app.test_client().get("/api/clients").status_code == 404
    assert client_app.test_client().get("/api/clients").status_code == 200
    assert client_app.test_client().get("/api/clients/1/workouts").status_code == 404
