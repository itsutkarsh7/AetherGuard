from app import create_app

app = create_app()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Launching AetherGuard - Advanced Cybersecurity Intelligence")
    print("=" * 60)
    app.run(debug=True)
