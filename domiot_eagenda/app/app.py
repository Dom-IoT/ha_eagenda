from flask import Flask, g, request, render_template
from config import Config
from flask_migrate import Migrate
from models import db, Category, Event, Status, Color
from utils import url_for, get_user_role, redirect
import datetime
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
    today = datetime.datetime.now()
    start = datetime.datetime.combine(today, datetime.datetime.min.time())
    end = datetime.datetime.combine(today, datetime.datetime.max.time())
    events = Event.query.filter(
        Event.start_dt >= start,
        Event.start_dt <= end,
        Event.all_day == False
    ).order_by(Event.start_dt).all()

    context = {
        'events': events,
        'all_day_events': Event.query.filter(Event.all_day == True).all()
    }
    return render_template('events/kiosk.html', **context)

@app.route('/healthcare_staff')
@roles_required(['healthcare_staff'])
def healthcare_staff():
    """
    Healthcare staff dashboard
    """
    events = Event.query.all()

    context = {
        'events': events,
    }

    return render_template('events/list.html', **context)

@app.route('/add', methods=['GET', 'POST'])
@roles_required(["healthcare_staff"], redirect_to='index')
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        all_day = request.form.get('all_day')

        if all_day:
            start = datetime.datetime.fromisoformat(request.form['start_dt'])
            end_dt = start + datetime.timedelta(days=1)
        else:
            start = datetime.datetime.fromisoformat(request.form['start_dt'])
            end_dt = datetime.datetime.fromisoformat(request.form['end_dt'])

        event = Event(
            title=title,
            status=Status.PENDING,
            description=description,
            all_day=all_day is not None,
            start_dt=start,
            end_dt=end_dt,
            color=Color(request.form['color']),
        )

        selected_category_ids = request.form.getlist('categories')
        for cid in selected_category_ids:
            category = Category.query.get(int(cid))
            if category:
                event.categories.append(category)

        db.session.add(event)
        db.session.commit()

        return redirect("patient")

    categories = Category.query.order_by(Category.name).all()
    return render_template('events/create.html', categories=categories, statuses=Status, colors=Color)

@app.route('/categories/create', methods=['POST'])
@roles_required(["healthcare_staff"], redirect_to='index')
def create_category():
    name = request.form.get('name')
    if not name:
        return "Category name is required", 400

    existing_category = Category.query.filter_by(name=name).first()
    if existing_category:
        return "Category already exists", 400

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()

    return {"id": category.id, "name": category.name}, 201

if __name__ == '__main__':
    app.run(debug=True)