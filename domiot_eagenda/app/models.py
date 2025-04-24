import enum
from datetime import datetime, timezone
from sqlalchemy import Enum, Table, Column, Integer, ForeignKey
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db: SQLAlchemy = SQLAlchemy()


class Status(enum.Enum):
    DONE = "done"
    PENDING = "pending"
    MISSED = "missed"

class Color(enum.Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    WARNING = "warning"
    DANGER = "danger"
    INFO = "info"
    DARK = "dark"
    LIGHT = "light"

event_category = Table(
    'event_category',
    db.Model.metadata,
    Column('event_id', Integer, ForeignKey('event.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('category.id'), primary_key=True)
)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    color = db.Column(Enum(Color), default=Color.PRIMARY, nullable=False)
    status = db.Column(Enum(Status), default=Status.PENDING, nullable=False)
    description = db.Column(db.Text, nullable=True)
    all_day = db.Column(db.Boolean, default=False, nullable=False)
    start_dt = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    end_dt = db.Column(db.DateTime, nullable=True)

    categories = relationship("Category", secondary=event_category, back_populates="events")

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    events = relationship("Event", secondary=event_category, back_populates="categories")
