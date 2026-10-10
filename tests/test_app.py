import math

import pytest

from app import (
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
