from flask import Flask, jsonify

app = Flask(__name__)

PROGRAMS = [
    {
        "name": "Fat Loss (FL)",
        "focus": "fat loss and metabolic conditioning",
        "daily_calories": 2000,
    },
    {
        "name": "Muscle Gain (MG)",
        "focus": "strength, size and recovery",
        "daily_calories": 3200,
    },
    {
        "name": "Beginner (BG)",
        "focus": "consistency, technique and confidence",
        "daily_calories": 2400,
    },
    {
        "name": "Performance (PR)",
        "focus": "speed, power and endurance",
        "daily_calories": 2800,
    },
]


@app.route("/")
def home():
    return jsonify(
        {
            "app": "ACEest Fitness & Gym",
            "status": "ok",
            "location": "Chennai, Tamil Nadu",
        }
    )


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "ACEest Fitness & Gym"})


@app.route("/api/programs")
def get_programs():
    return jsonify({"programs": PROGRAMS})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
