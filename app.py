import math
import os
import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

from flask import Flask, current_app, g, jsonify, request
from werkzeug.exceptions import BadRequest, NotFound

PROGRAMS = {
    "Fat Loss (FL)": {
        "description": "Progressive strength and conditioning for sustainable fat loss.",
        "workout": [
            "Mon: Lower-body strength",
            "Tue: Zone 2 cardio and mobility",
            "Wed: Upper-body strength",
            "Thu: Recovery walk",
            "Fri: Full-body circuit",
            "Sat: Optional easy cardio",
            "Sun: Rest",
        ],
        "diet": [
            "Breakfast: Egg whites, oats and fruit",
            "Lunch: Grilled chicken, brown rice and salad",
            "Dinner: Fish curry, millet roti and greens",
        ],
        "meals": [
            {"meal": "Breakfast", "foods": "Egg whites, oats and fruit", "calories": 450, "protein_g": 32},
            {"meal": "Lunch", "foods": "Grilled chicken, brown rice and salad", "calories": 650, "protein_g": 48},
            {"meal": "Snack", "foods": "Curd and a banana", "calories": 250, "protein_g": 12},
            {"meal": "Dinner", "foods": "Fish curry, millet roti and greens", "calories": 600, "protein_g": 42},
        ],
        "exercises": [
            {"name": "Back squat", "sets": 4, "reps": "6-8", "rest_seconds": 120, "focus": "Controlled lower-body strength"},
            {"name": "Romanian deadlift", "sets": 3, "reps": "8-10", "rest_seconds": 90, "focus": "Hip hinge and hamstrings"},
            {"name": "Stationary bike", "sets": 1, "reps": "15 minutes", "rest_seconds": 0, "focus": "Moderate aerobic conditioning"},
        ],
        "daily_calories": 2000,
        "focus": "fat loss and metabolic conditioning",
    },
    "Muscle Gain (MG)": {
        "description": "Progressive resistance training with recovery-focused nutrition.",
        "workout": [
            "Mon: Push - chest, shoulders and triceps",
            "Tue: Pull - back and biceps",
            "Wed: Legs",
            "Thu: Rest and mobility",
            "Fri: Upper-body hypertrophy",
            "Sat: Lower-body strength",
            "Sun: Recovery",
        ],
        "diet": [
            "Breakfast: Eggs, oats and banana",
            "Lunch: Chicken rice bowl with vegetables",
            "Dinner: Paneer, rice, dal and salad",
        ],
        "meals": [
            {"meal": "Breakfast", "foods": "Eggs, oats and banana", "calories": 650, "protein_g": 36},
            {"meal": "Lunch", "foods": "Chicken rice bowl with vegetables", "calories": 850, "protein_g": 52},
            {"meal": "Snack", "foods": "Greek yogurt, nuts and fruit", "calories": 400, "protein_g": 24},
            {"meal": "Dinner", "foods": "Paneer, rice, dal and salad", "calories": 800, "protein_g": 38},
        ],
        "exercises": [
            {"name": "Barbell bench press", "sets": 4, "reps": "6-8", "rest_seconds": 150, "focus": "Horizontal pressing strength"},
            {"name": "Lat pulldown", "sets": 4, "reps": "8-12", "rest_seconds": 90, "focus": "Back and lats"},
            {"name": "Goblet squat", "sets": 4, "reps": "8-10", "rest_seconds": 120, "focus": "Leg strength and technique"},
        ],
        "daily_calories": 3200,
        "focus": "strength, size and recovery",
    },
    "Beginner (BG)": {
        "description": "A sustainable introduction to strength, movement and recovery.",
        "workout": [
            "Mon: Full-body basics",
            "Tue: Easy walk and mobility",
            "Wed: Full-body basics",
            "Thu: Rest",
            "Fri: Full-body basics",
            "Sat: Optional light activity",
            "Sun: Recovery",
        ],
        "diet": [
            "Breakfast: Idli-sambar and fruit",
            "Lunch: Rice, dal, vegetables and curd",
            "Dinner: Chapati, vegetables and paneer",
        ],
        "meals": [
            {"meal": "Breakfast", "foods": "Idli-sambar and fruit", "calories": 450, "protein_g": 16},
            {"meal": "Lunch", "foods": "Rice, dal, vegetables and curd", "calories": 700, "protein_g": 24},
            {"meal": "Snack", "foods": "Sundal and buttermilk", "calories": 250, "protein_g": 12},
            {"meal": "Dinner", "foods": "Chapati, vegetables and paneer", "calories": 650, "protein_g": 28},
        ],
        "exercises": [
            {"name": "Chair squat", "sets": 3, "reps": "8-10", "rest_seconds": 90, "focus": "Learn squat pattern safely"},
            {"name": "Incline push-up", "sets": 3, "reps": "6-10", "rest_seconds": 60, "focus": "Upper-body pushing technique"},
            {"name": "Supported dumbbell row", "sets": 3, "reps": "8-10 per side", "rest_seconds": 60, "focus": "Upper-back strength"},
        ],
        "daily_calories": 2400,
        "focus": "consistency, technique and confidence",
    },
    "Performance (PR)": {
        "description": "Strength, speed and aerobic work for recreational athletes.",
        "workout": [
            "Mon: Lower-body strength and jumps",
            "Tue: Tempo run and mobility",
            "Wed: Upper-body strength",
            "Thu: Recovery",
            "Fri: Sprint intervals",
            "Sat: Sport practice or easy endurance",
            "Sun: Rest",
        ],
        "diet": [
            "Breakfast: Poha with eggs and fruit",
            "Lunch: Chicken rice bowl with vegetables",
            "Dinner: Tandoori fish, quinoa and salad",
        ],
        "meals": [
            {"meal": "Breakfast", "foods": "Poha with eggs and fruit", "calories": 600, "protein_g": 28},
            {"meal": "Lunch", "foods": "Chicken rice bowl with vegetables", "calories": 750, "protein_g": 48},
            {"meal": "Snack", "foods": "Banana and yogurt", "calories": 300, "protein_g": 14},
            {"meal": "Dinner", "foods": "Tandoori fish, quinoa and salad", "calories": 750, "protein_g": 46},
        ],
        "exercises": [
            {"name": "Box jump", "sets": 4, "reps": "4", "rest_seconds": 120, "focus": "Explosive power; use a safe box height"},
            {"name": "Trap-bar deadlift", "sets": 4, "reps": "4-6", "rest_seconds": 150, "focus": "Full-body strength"},
            {"name": "Tempo run", "sets": 1, "reps": "20 minutes", "rest_seconds": 0, "focus": "Controlled aerobic threshold"},
        ],
        "daily_calories": 2800,
        "focus": "speed, power and endurance",
    },
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL COLLATE NOCASE UNIQUE,
    age INTEGER NOT NULL CHECK (age BETWEEN 1 AND 120),
    height_cm REAL NOT NULL CHECK (height_cm > 0),
    weight_kg REAL NOT NULL CHECK (weight_kg > 0),
    goal TEXT NOT NULL,
    experience TEXT NOT NULL DEFAULT 'beginner',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    workout_type TEXT NOT NULL,
    duration_min INTEGER NOT NULL CHECK (duration_min > 0),
    workout_date TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    weight_kg REAL NOT NULL CHECK (weight_kg > 0),
    adherence_pct INTEGER NOT NULL CHECK (adherence_pct BETWEEN 0 AND 100),
    notes TEXT NOT NULL DEFAULT '',
    recorded_at TEXT NOT NULL
);
"""


def calculate_bmi(height_cm, weight_kg):
    if (
        not math.isfinite(height_cm)
        or not math.isfinite(weight_kg)
        or height_cm <= 0
        or weight_kg <= 0
    ):
        raise ValueError("Height and weight must be finite values greater than zero.")
    return round(weight_kg / ((height_cm / 100) ** 2), 2)


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
    return {"name": name, **PROGRAMS[name]}


def build_weekly_schedule(plan_name):
    program = PROGRAMS[plan_name]
    return {
        "program": plan_name,
        "focus": program["focus"],
        "days": program["workout"],
        "nutrition": program["diet"],
        "exercises": program["exercises"],
        "meals": program["meals"],
    }


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_db():
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(_error=None):
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db(app):
    database = app.config["DATABASE"]
    Path(database).parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database)
    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.executescript(SCHEMA)
        connection.commit()
    finally:
        connection.close()


def request_object():
    if not request.is_json:
        raise BadRequest("Request body must use the application/json content type.")
    payload = request.get_json()
    if not isinstance(payload, dict):
        raise BadRequest("Request body must be a JSON object.")
    return payload


def required_text(payload, key, max_length=200):
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise BadRequest(f"'{key}' must be a non-empty string.")
    value = value.strip()
    if len(value) > max_length:
        raise BadRequest(f"'{key}' must be at most {max_length} characters.")
    return value


def positive_number(payload, key):
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise BadRequest(f"'{key}' must be a number greater than zero.")
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise BadRequest(f"'{key}' must be a finite number greater than zero.")
    return value


def positive_integer(payload, key, maximum=None):
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise BadRequest(f"'{key}' must be a positive integer.")
    if maximum is not None and value > maximum:
        raise BadRequest(f"'{key}' must not exceed {maximum}.")
    return value


def optional_notes(payload):
    value = payload.get("notes", "")
    if not isinstance(value, str) or len(value) > 1000:
        raise BadRequest("'notes' must be a string of at most 1000 characters.")
    return value.strip()


def serialize_client(row):
    result = dict(row)
    result["bmi"] = calculate_bmi(result["height_cm"], result["weight_kg"])
    result["bmi_category"] = bmi_category(result["bmi"])
    result["target_calories"] = calculate_target_calories(
        result["weight_kg"], result["goal"]
    )
    return result


def get_client_or_404(client_id):
    client = get_db().execute(
        "SELECT * FROM clients WHERE id = ?", (client_id,)
    ).fetchone()
    if client is None:
        raise NotFound("Client not found.")
    return client


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, "aceest_fitness.db"),
        ENABLE_CLIENTS=True,
        ENABLE_ACTIVITY_TRACKING=True,
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)
    init_db(app)
    app.teardown_appcontext(close_db)

    @app.errorhandler(BadRequest)
    def handle_bad_request(error):
        return jsonify({"error": error.description}), 400

    @app.errorhandler(NotFound)
    def handle_not_found(error):
        return jsonify({"error": error.description}), 404

    @app.errorhandler(sqlite3.IntegrityError)
    def handle_integrity_error(_error):
        return jsonify({"error": "A record conflicts with existing data."}), 409

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

    @app.before_request
    def enforce_version_features():
        if request.path.startswith("/api/clients"):
            if not app.config["ENABLE_CLIENTS"]:
                raise NotFound("Client management is not available in this version.")
            if (
                not app.config["ENABLE_ACTIVITY_TRACKING"]
                and request.path.rsplit("/", 1)[-1] in {"workouts", "progress"}
            ):
                raise NotFound("Activity tracking is not available in this version.")

    @app.route("/")
    def home():
        return jsonify(
            {
                "app": "ACEest Fitness & Gym",
                "status": "ok",
                "location": "Chennai, Tamil Nadu",
                "features": [
                    "Detailed exercise and meal plans",
                    "BMI and calorie guidance",
                    "Client profile management",
                    "Workout logging and progress tracking",
                ],
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
        height_cm = query_value("height", 175.0, float)
        weight_kg = query_value("weight", 70.0, float)
        age = query_value("age", 28, int)
        experience = request.args.get("experience", "beginner")
        bmi = calculate_bmi(height_cm, weight_kg)
        program = suggest_program(goal, experience)
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
                "recommended_plan": suggest_program(goal),
                "target_calories": calculate_target_calories(weight_kg, goal),
            }
        )

    @app.route("/api/clients", methods=["GET", "POST"])
    def clients():
        db = get_db()
        if request.method == "GET":
            rows = db.execute("SELECT * FROM clients ORDER BY id").fetchall()
            return jsonify({"clients": [serialize_client(row) for row in rows]})

        payload = request_object()
        name = required_text(payload, "name", 100)
        age = positive_integer(payload, "age", 120)
        height_cm = positive_number(payload, "height_cm")
        weight_kg = positive_number(payload, "weight_kg")
        goal = required_text(payload, "goal", 100)
        experience = payload.get("experience", "beginner")
        if not isinstance(experience, str) or not experience.strip():
            raise BadRequest("'experience' must be a non-empty string.")
        cursor = db.execute(
            """
            INSERT INTO clients (name, age, height_cm, weight_kg, goal, experience, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (name, age, height_cm, weight_kg, goal, experience.strip(), utc_now()),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM clients WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return jsonify({"client": serialize_client(row)}), 201

    @app.route("/api/clients/<int:client_id>", methods=["GET", "PUT", "DELETE"])
    def client_detail(client_id):
        db = get_db()
        current = get_client_or_404(client_id)
        if request.method == "GET":
            return jsonify({"client": serialize_client(current)})
        if request.method == "DELETE":
            db.execute("DELETE FROM clients WHERE id = ?", (client_id,))
            db.commit()
            return "", 204

        payload = request_object()
        name = required_text(payload, "name", 100)
        age = positive_integer(payload, "age", 120)
        height_cm = positive_number(payload, "height_cm")
        weight_kg = positive_number(payload, "weight_kg")
        goal = required_text(payload, "goal", 100)
        experience = payload.get("experience", current["experience"])
        if not isinstance(experience, str) or not experience.strip():
            raise BadRequest("'experience' must be a non-empty string.")
        db.execute(
            """
            UPDATE clients
            SET name = ?, age = ?, height_cm = ?, weight_kg = ?, goal = ?, experience = ?
            WHERE id = ?
            """,
            (name, age, height_cm, weight_kg, goal, experience.strip(), client_id),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM clients WHERE id = ?", (client_id,)
        ).fetchone()
        return jsonify({"client": serialize_client(row)})

    @app.route(
        "/api/clients/<int:client_id>/workouts", methods=["GET", "POST"]
    )
    def client_workouts(client_id):
        get_client_or_404(client_id)
        db = get_db()
        if request.method == "GET":
            rows = db.execute(
                "SELECT * FROM workouts WHERE client_id = ? ORDER BY workout_date DESC, id DESC",
                (client_id,),
            ).fetchall()
            return jsonify({"workouts": [dict(row) for row in rows]})

        payload = request_object()
        workout_type = required_text(payload, "workout_type", 100)
        duration_min = positive_integer(payload, "duration_min", 1440)
        workout_date = payload.get("workout_date", date.today().isoformat())
        if not isinstance(workout_date, str):
            raise BadRequest("'workout_date' must use YYYY-MM-DD format.")
        try:
            workout_date = date.fromisoformat(workout_date).isoformat()
        except ValueError as error:
            raise BadRequest("'workout_date' must use YYYY-MM-DD format.") from error
        cursor = db.execute(
            """
            INSERT INTO workouts (client_id, workout_type, duration_min, workout_date, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                client_id,
                workout_type,
                duration_min,
                workout_date,
                optional_notes(payload),
                utc_now(),
            ),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM workouts WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return jsonify({"workout": dict(row)}), 201

    @app.route(
        "/api/clients/<int:client_id>/progress", methods=["GET", "POST"]
    )
    def client_progress(client_id):
        get_client_or_404(client_id)
        db = get_db()
        if request.method == "GET":
            rows = db.execute(
                "SELECT * FROM progress WHERE client_id = ? ORDER BY id DESC",
                (client_id,),
            ).fetchall()
            return jsonify({"progress": [dict(row) for row in rows]})

        payload = request_object()
        weight_kg = positive_number(payload, "weight_kg")
        adherence_pct = payload.get("adherence_pct")
        if (
            isinstance(adherence_pct, bool)
            or not isinstance(adherence_pct, int)
            or not 0 <= adherence_pct <= 100
        ):
            raise BadRequest("'adherence_pct' must be an integer from 0 to 100.")
        cursor = db.execute(
            """
            INSERT INTO progress (client_id, weight_kg, adherence_pct, notes, recorded_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (client_id, weight_kg, adherence_pct, optional_notes(payload), utc_now()),
        )
        db.commit()
        row = db.execute(
            "SELECT * FROM progress WHERE id = ?", (cursor.lastrowid,)
        ).fetchone()
        return jsonify({"progress": dict(row)}), 201

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
