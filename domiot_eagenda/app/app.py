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
    logging.info(f"CORE_ADDON_HOSTNAME: {app.config['CORE_ADDON_HOSTNAME']}")

    user = request.headers.get('X-Remote-User-Name')
    role = get_user_role(user)

    if role == 'patient':
        return redirect('patient')

    elif role == 'healthcare_staff':
        return redirect('healthcare_staff')

    else:
        return redirect('noaccess')


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


@app.route('/api/events/<event_id>/', methods=['POST'])
@roles_required(['patient', 'healthcare_staff'])
def update_status(event_id):
    """
    API endpoint to update the status of an event
    """
    event = Event.query.get(event_id)
    if not event:
        return "Event not found", 404

    status = request.form.get('status')
    if status:
        event.status = Status[status]
        db.session.commit()
        return {"status": "success"}, 200
    else:
        return "Invalid status", 400



@app.route('/api/events/', methods=['GET'])
@roles_required(['patient', 'healthcare_staff'])
def list_events_json():
    """
    API endpoint to list events in JSON format
    """
    event_list = []
    all_day_events_list = []

    arg_start = request.args.get('start')
    arg_end = request.args.get('end')

    if arg_start:
        if arg_end:
            events = Event.query.filter(
                Event.all_day == False,
                Event.start_dt >= datetime.datetime.fromisoformat(arg_start),
                Event.start_dt <= datetime.datetime.fromisoformat(arg_end)
            ).order_by(Event.start_dt).all()
            all_day_events = Event.query.filter(
                Event.all_day == True,
                Event.start_dt >= datetime.datetime.fromisoformat(arg_start),
                Event.start_dt <= datetime.datetime.fromisoformat(arg_end)
            ).order_by(Event.start_dt).all()
        else:
            events = Event.query.filter(
                Event.all_day == False,
                Event.start_dt >= datetime.datetime.fromisoformat(arg_start)
            ).order_by(Event.start_dt).all()
            all_day_events = Event.query.filter(
                Event.all_day == True,
                Event.start_dt >= datetime.datetime.fromisoformat(arg_start)
            ).order_by(Event.start_dt).all()
    elif arg_end:
        events = Event.query.filter(
            Event.all_day == False,
            Event.start_dt <= datetime.datetime.fromisoformat(arg_end)
        ).order_by(Event.start_dt).all()
        all_day_events = Event.query.filter(
            Event.all_day == True,
            Event.start_dt <= datetime.datetime.fromisoformat(arg_end)
        ).order_by(Event.start_dt).all()
    else:
        events = Event.query.filter(Event.all_day == False).all()
        all_day_events = Event.query.filter(Event.all_day == True).all()

    for event in events:
        event_list.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_dt': event.start_dt.isoformat(),
            'end_dt': event.end_dt.isoformat(),
            'status': event.status.name,
            'color': event.color.value,
            'categories': [category.name for category in event.categories]
        })

    for event in all_day_events:
        all_day_events_list.append({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'start_dt': event.start_dt.isoformat(),
            'end_dt': event.end_dt.isoformat(),
            'status': event.status.name,
            'color': event.color.value,
            'categories': [category.name for category in event.categories]
        })

    return {"events": event_list, "all_day_events": all_day_events_list}


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

@app.route('/edit/<event_id>/', methods=['GET', 'POST'])
@roles_required(["healthcare_staff"], redirect_to='index')
def edit_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return "Event not found", 404

    if request.method == 'POST':
        # Update the existing event's attributes
        event.title = request.form['title']
        event.description = request.form.get('description')
        event.all_day = request.form.get('all_day') is not None

        if event.all_day:
            event.start_dt = datetime.datetime.fromisoformat(request.form['start_dt'])
            event.end_dt = event.start_dt + datetime.timedelta(days=1)
        else:
            event.start_dt = datetime.datetime.fromisoformat(request.form['start_dt'])
            event.end_dt = datetime.datetime.fromisoformat(request.form['end_dt'])

        event.color = Color(request.form['color'])

        # Update categories
        event.categories.clear()
        selected_category_ids = request.form.getlist('categories')
        for cid in selected_category_ids:
            category = Category.query.get(int(cid))
            if category:
                event.categories.append(category)

        db.session.commit()
        return redirect("healthcare_staff")

    categories = Category.query.order_by(Category.name).all()
    return render_template('events/edit.html', event=event, categories=categories, statuses=Status, colors=Color)


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



@app.route('/noaccess')
def no_access():
    return render_template('no_access.html')


@app.route("/missconfig")
def missconfig():
    return render_template('missconfig.html')


if __name__ == '__main__':
    app.run(debug=True)
