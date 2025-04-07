import sqlite3
import fastapi
import os
from pydantic import BaseModel
from enum import IntEnum
from datetime import datetime
from typing import List, Optional


if not os.path.exists("db.sqlite"):
    # Create a new SQLite database file if it doesn't exist
    open('db.sqlite', 'w').close()
    con = sqlite3.connect('db.sqlite', check_same_thread=False)
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_dt TEXT NOT NULL,
            end_dt TEXT NOT NULL,
            rrule TEXT,
            ha_user_id INTEGER,
            status INTEGER DEFAULT 1
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS event_categories (
            event_id INTEGER,
            category_id INTEGER,
            FOREIGN KEY(event_id) REFERENCES events(id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
    """)
    con.commit()

class Status(IntEnum):
    pending = 1
    done = 2
    missed = 3

class Category(BaseModel):
    id: int
    name: str

class Event(BaseModel):
    id: int
    name: str
    description: str
    start_dt: datetime
    end_dt: datetime
    rrule: Optional[str]
    ha_user_id: int
    status: Status = Status.pending
    categories: List[Category] = []

class EventDTO(BaseModel):
    name: str
    description: Optional[str] = None
    start_dt: datetime
    end_dt: datetime
    rrule: Optional[str] = None
    ha_user_id: int
    status: Status = Status.pending

con = sqlite3.connect('db.sqlite', check_same_thread=False)
cur = con.cursor()

app = fastapi.FastAPI()


@app.get("/events/")
def list_events():
    cur.execute("SELECT * FROM events")
    results = []
    events = cur.fetchall()
    for event in events:
        results.append({
            "id": event[0],
            "name": event[1],
            "description": event[2],
            "start_dt": event[3],
            "end_dt": event[4],
            "rrule": event[5],
            "ha_user_id": event[6],
            "status": Status(event[7]),
        })
    return results

@app.get("/events/{event_id}")
def get_event(event_id: int):
    cur.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = cur.fetchone()

    if event:
        return {
            "id": event[0],
            "name": event[1],
            "description": event[2],
            "start_dt": event[3],
            "end_dt": event[4],
            "rrule": event[5],
            "ha_user_id": event[6],
            "status": Status(event[7]),
        }
    else:
        return {"error": "Event not found"}
    
@app.post("/events/")
def create_event(event: EventDTO):
    # Create an event based on the provided DTO
    cur.execute("""
        INSERT INTO events (name, description, start_dt, end_dt, rrule, ha_user_id)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (event.name, event.description, event.start_dt, event.end_dt, event.rrule, event.ha_user_id))
    con.commit()
    event_id = cur.lastrowid
    

    return event
