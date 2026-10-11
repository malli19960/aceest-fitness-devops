from app import create_app

app = create_app(
    {
        "ENABLE_CLIENTS": False,
        "ENABLE_ACTIVITY_TRACKING": False,
    }
)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
