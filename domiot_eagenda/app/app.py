from flask import Flask, g, request, render_template
from config import Config
from flask_migrate import Migrate
from models import db
from utils import url_for, get_user_role, redirect
from decorators import roles_required
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
    user = request.headers.get('X-Remote-User-Name')
    role = get_user_role(user)

    if role == 'patient':
        return redirect('patient')
    
    elif role == 'healthcare_staff':
        return redirect('healthcare_staff')

    else:
        return "Hello, World!"
    
@app.route('/patient')
@roles_required(['patient'])
def patient():
    """
    Patient dashboard
    """
    return render_template('patient.html')

@app.route('/healthcare_staff')
@roles_required(['healthcare_staff'])
def healthcare_staff():
    """
    Healthcare staff dashboard
    """
    return render_template('healthcare_staff.html')