from app import create_app

# Flask app entrypoint used by local `python run.py`.
app = create_app()

if __name__ == "__main__":
    # Debug is enabled for local development convenience.
    app.run(debug=True)