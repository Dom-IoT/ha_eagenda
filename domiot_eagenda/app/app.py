from flask import Flask
from config import Config
from flask_migrate import Migrate

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/')
def index():
    return "Hello, World!"