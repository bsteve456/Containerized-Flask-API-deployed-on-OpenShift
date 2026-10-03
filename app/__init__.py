from flask import Flask
from app.models import db
import os

app = Flask(__name__)

# Database Configuration
# Use SQLite for local dev (no psycopg needed), PostgreSQL for production
database_url = os.getenv('DATABASE_URL')
if not database_url:
    # Local development: SQLite
    database_url = 'sqlite:///task_manager.db'

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables on startup
with app.app_context():
    db.create_all()

# Import routes to register endpoints
from app import routes