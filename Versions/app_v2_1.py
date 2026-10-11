import math

from flask import Flask, jsonify, request
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

PROGRAMS = {
    "Fat Loss (FL)": {
        "focus": "fat loss and metabolic conditioning",
        "daily_calories": 2000,
        "workout": ["Strength training", "Conditioning", "Active recovery"],
    },
    "Muscle Gain (MG)": {
        "focus": "strength, size and recovery",
        "daily_calories": 3200,
        "workout": ["Push day", "Pull day", "Leg day"],
    },
    "Beginner (BG)": {
        "focus": "consistency, technique and confidence",
        "daily_calories": 2400,
        "workout": ["Full body basics", "Walking", "Mobility"],
    },
    "Performance (PR)": {
        "focus": "speed, power and endurance",
        "daily_calories": 2800,
        "workout": ["Power training", "Tempo run", "Sprint conditioning"],
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
    return round(weight_kg / ((height_cm / 100) ** 2), 2)


def bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def calculate_target_calories(weight_kg, goal):
    if not math.isfinite(weight_kg) or weight_kg <= 0:
        raise ValueError("Weight must be a finite value greater than zero.")
    base = weight_kg * 30
    goal = (goal or "").strip().lower()
    if "fat" in goal or "loss" in goal:
        return int(base - 250)
    if "muscle" in goal or "gain" in goal or "strength" in goal:
        return int(base + 300)
    return int(base + 100)


def suggest_program(goal):
    normalized = (goal or "").strip().lower()
    if "fat" in normalized or "loss" in normalized:
        name = "Fat Loss (FL)"
    elif "muscle" in normalized or "gain" in normalized or "strength" in normalized:
        name = "Muscle Gain (MG)"
    elif "performance" in normalized or "sport" in normalized or "athlete" in normalized:
        name = "Performance (PR)"
    else:
        name = "Beginner (BG)"
    return {"name": name, **PROGRAMS[name]}


def positive_query_value(name, default, converter):
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
            "features": ["Program recommendations", "BMI and calorie guidance"],
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "ACEest Fitness & Gym"})


@app.route("/api/programs")
def get_programs():
    return jsonify(
        {"programs": [{"name": name, **details} for name, details in PROGRAMS.items()]}
    )


@app.route("/api/plan")
def plan():
    goal = request.args.get("goal", "fat loss")
    height_cm = positive_query_value("height", 175.0, float)
    weight_kg = positive_query_value("weight", 70.0, float)
    age = positive_query_value("age", 28, int)
    bmi = calculate_bmi(height_cm, weight_kg)
    program = suggest_program(goal)
    return jsonify(
        {
            "goal": goal.lower(),
            "age": age,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "bmi": bmi,
            "bmi_category": bmi_category(bmi),
            "target_calories": calculate_target_calories(weight_kg, goal),
            "program": program,
            "weekly_schedule": {
                "program": program["name"],
                "focus": program["focus"],
                "days": program["workout"],
            },
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
