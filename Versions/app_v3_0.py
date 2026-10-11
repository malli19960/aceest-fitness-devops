import math

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest

PROGRAMS = {
    "Fat Loss (FL)": {
        "description": "High-energy fat-loss system built for busy professionals in Chennai and nearby cities.",
        "workout": [
            "Mon: 5x5 Back Squat + EMOM bike intervals",
            "Tue: Upper body strength + 20-minute brisk walk",
            "Wed: Circuit conditioning + core work",
            "Thu: Deadlift + sprint intervals",
            "Fri: Full body circuit + mobility",
            "Sat: Active recovery and stretch",
        ],
        "diet": [
            "Breakfast: Egg white oats and fruit",
            "Lunch: Grilled chicken, brown rice, salad",
            "Dinner: Fish curry with millet roti and greens",
        ],
        "daily_calories": 2000,
        "focus": "fat loss and metabolic conditioning",
    },
    "Muscle Gain (MG)": {
        "description": "Lean muscle-building block focused on progressive overload and recovery.",
        "workout": [
            "Mon: Push day",
            "Tue: Pull day",
            "Wed: Legs",
            "Thu: Rest and mobility",
            "Fri: Upper body hypertrophy",
            "Sat: Lower body strength",
            "Sun: Recovery",
        ],
        "diet": [
            "Breakfast: 4 eggs, oats, banana",
            "Lunch: Chicken biryani with vegetables",
            "Dinner: Paneer, rice, dal and salad",
        ],
        "daily_calories": 3200,
        "focus": "strength, size and recovery",
    },
    "Beginner (BG)": {
        "description": "A steady, sustainable routine for first-time gym members and adolescent athletes.",
        "workout": [
            "Mon: Full body basics",
            "Tue: Mobility and walking",
            "Wed: Full body basics",
            "Thu: Rest",
            "Fri: Full body basics",
            "Sat: Light conditioning",
            "Sun: Recovery",
        ],
        "diet": [
            "Breakfast: Idli-sambar and fruit",
            "Lunch: Rice, dal and curd",
            "Dinner: Chapati, vegetables and paneer",
        ],
        "daily_calories": 2400,
        "focus": "consistency, technique and confidence",
    },
    "Performance (PR)": {
        "description": "Performance-focused plan for athletes needing explosive power and work capacity.",
        "workout": [
            "Mon: Power clean + vertical jumps",
            "Tue: Tempo run + mobility",
            "Wed: Upper force block",
            "Thu: Lower strength block",
            "Fri: Sprint conditioning",
            "Sat: Team sport or testing day",
        ],
        "diet": [
            "Breakfast: Poha with eggs and fruit",
            "Lunch: Chicken rice bowl with vegetables",
            "Dinner: Tandoori fish plus quinoa and salad",
        ],
        "daily_calories": 2800,
        "focus": "speed, power and endurance",
    },
}


def calculate_bmi(height_cm, weight_kg):
    if (
        not math.isfinite(height_cm)
        or not math.isfinite(weight_kg)
        or height_cm <= 0
        or weight_kg <= 0
    ):
        raise ValueError("Height and weight must be finite values greater than zero.")
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m**2), 2)


def bmi_category(bmi_value):
    if bmi_value < 18.5:
        return "Underweight"
    if bmi_value < 25:
        return "Normal"
    if bmi_value < 30:
        return "Overweight"
    return "Obese"


def calculate_target_calories(weight_kg, goal):
    if not math.isfinite(weight_kg) or weight_kg <= 0:
        raise ValueError("Weight must be a finite value greater than zero.")
    base = weight_kg * 30
    goal_key = (goal or "").strip().lower()
    if "fat" in goal_key or "loss" in goal_key:
        return int(base - 250)
    if "muscle" in goal_key or "gain" in goal_key or "strength" in goal_key:
        return int(base + 300)
    return int(base + 100)


def suggest_program(goal, experience_level="beginner"):
    normalized = (goal or "").strip().lower()
    if "fat" in normalized or "loss" in normalized:
        name = "Fat Loss (FL)"
    elif "muscle" in normalized or "gain" in normalized or "strength" in normalized:
        name = "Muscle Gain (MG)"
    elif "performance" in normalized or "sport" in normalized or "athlete" in normalized:
        name = "Performance (PR)"
    else:
        name = "Beginner (BG)"

    plan = PROGRAMS[name].copy()
    plan["name"] = name
    return plan


def build_weekly_schedule(plan_name):
    program = PROGRAMS[plan_name]
    return {
        "program": plan_name,
        "focus": program["focus"],
        "days": program["workout"],
        "nutrition": program["diet"],
    }


def create_app():
    app = Flask(__name__)

    def query_value(name, default, converter):
        raw_value = request.args.get(name)
        if raw_value is None:
            return default
        try:
            value = converter(raw_value)
        except ValueError as error:
            raise BadRequest(f"'{name}' must be a valid {converter.__name__}.") from error
        if value <= 0 or isinstance(value, float) and not math.isfinite(value):
            raise BadRequest(f"'{name}' must be a finite value greater than zero.")
        return value

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify({"error": error.description}), 400

    @app.route("/")
    def home():
        return jsonify(
            {
                "app": "ACEest Fitness & Gym",
                "status": "ok",
                "location": "Chennai, Tamil Nadu",
                "features": [
                    "Personalized fitness programming",
                    "BMI and calorie guidance",
                    "Weekly workout scheduling",
                    "Nutrition recommendations",
                ],
            }
        )

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "ACEest Fitness & Gym"})

    @app.route("/api/programs")
    def get_programs():
        return jsonify(
            {
                "programs": [
                    {"name": name, **details} for name, details in PROGRAMS.items()
                ]
            }
        )

    @app.route("/api/plan")
    def plan():
        goal = request.args.get("goal", "fat loss")
        height_cm = query_value("height", 175.0, float)
        weight_kg = query_value("weight", 70.0, float)
        age = query_value("age", 28, int)
        experience = request.args.get("experience", "beginner")

        bmi = calculate_bmi(height_cm, weight_kg)
        program = suggest_program(goal, experience)
        calories = calculate_target_calories(weight_kg, goal)

        return jsonify(
            {
                "goal": goal.lower(),
                "age": age,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "bmi": bmi,
                "bmi_category": bmi_category(bmi),
                "target_calories": calories,
                "program": program,
                "weekly_schedule": build_weekly_schedule(program["name"]),
            }
        )

    @app.route("/api/summary")
    def summary():
        goal = request.args.get("goal", "fat loss")
        height_cm = query_value("height", 170.0, float)
        weight_kg = query_value("weight", 68.0, float)
        age = query_value("age", 25, int)

        bmi = calculate_bmi(height_cm, weight_kg)
        plan = suggest_program(goal)

        return jsonify(
            {
                "client_profile": {
                    "goal": goal.lower(),
                    "age": age,
                    "height_cm": height_cm,
                    "weight_kg": weight_kg,
                    "bmi": bmi,
                    "bmi_category": bmi_category(bmi),
                },
                "recommended_plan": plan,
                "target_calories": calculate_target_calories(weight_kg, goal),
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
