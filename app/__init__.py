from flask import Flask
from app.models import db
import os

app = Flask(__name__)

# Database Configuration
# Use in-memory SQLite for demos/containers, filesystem SQLite for local dev, PostgreSQL for production
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Container/Demo: use in-memory SQLite (no filesystem writes needed)
    # This works in read-only container filesystems and is perfect for testing
    database_url = 'sqlite:///:memory:'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables on startup (gracefully handle connection errors)
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    # Database not available on startup - will retry on first request
    print(f"[WARNING] Could not initialize database on startup: {e}")
    print("[WARNING] Database tables will be created on first request")

# Import routes to register endpoints
from app import routes