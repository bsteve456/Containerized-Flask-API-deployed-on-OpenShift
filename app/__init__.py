from flask import Flask

app = Flask(__name__)

# Import routes to register endpoints
from app import routes