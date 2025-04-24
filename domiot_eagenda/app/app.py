from flask import Flask
from config import Config
from flask_migrate import Migrate
from models import db
from utils import url_for
import logging

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

logging.basicConfig(level=logging.DEBUG)


@app.context_processor
def inject_url_for():
    """
    Inject the `url_for` monkeypatch into the template context. 
    use the `url_for` function in the templates.
    """
    return dict(url_for=url_for)

@app.route('/')
def index():
    return "Hello, World!"