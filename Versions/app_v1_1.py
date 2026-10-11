from flask import Flask, jsonify

app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
