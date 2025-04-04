import sqlite3
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

DATABASE = 'calendar.db'

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enum pour le statut
class Status(str):
    pending = "pending"
    done = "done"
    missed = "missed"

# Modèle de catégorie
class Category(BaseModel):
    id: Optional[int] = None
    name: str

# Modèle d'événement
class Event(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    start_dt: datetime
    end_dt: datetime
    rrule: str
    ha_user_id: int
    status: Status = Status.pending
    categories: List[Category] = []

# Fonction pour exécuter des requêtes SQL

def execute_query(query, args=(), fetchone=False, commit=False):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute(query, args)
    if commit:
        conn.commit()
        conn.close()
        return
    result = cursor.fetchone() if fetchone else cursor.fetchall()
    conn.close()
    return result

# Initialisation de la base de données
def init_db():
    queries = [
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            start_dt TEXT NOT NULL,
            end_dt TEXT NOT NULL,
            rrule TEXT,
            ha_user_id INTEGER,
            status TEXT DEFAULT 'pending'
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS event_categories (
            event_id INTEGER,
            category_id INTEGER,
            FOREIGN KEY(event_id) REFERENCES events(id),
            FOREIGN KEY(category_id) REFERENCES categories(id)
        )
        """
    ]
    for query in queries:
        execute_query(query, commit=True)

@app.get("/events/", response_model=List[Event])
def get_events():
    rows = execute_query("SELECT * FROM events")
    events = []
    for row in rows:
        event_id = row["id"]
        cat_rows = execute_query("""
            SELECT c.id, c.name FROM categories c
            JOIN event_categories ec ON c.id = ec.category_id
            WHERE ec.event_id = ?
        """, (event_id,))
        categories = [Category(id=cat["id"], name=cat["name"]) for cat in cat_rows]
        events.append(Event(
            id=row["id"],
            name=row["name"],
            description=row["description"],
            start_dt=datetime.fromisoformat(row["start_dt"]),
            end_dt=datetime.fromisoformat(row["end_dt"]),
            rrule=row["rrule"],
            ha_user_id=row["ha_user_id"],
            status=row["status"],
            categories=categories
        ))
    return events

@app.get("/events/{event_id}", response_model=Event)
def get_event(event_id: int):
    row = execute_query("SELECT * FROM events WHERE id = ?", (event_id,), fetchone=True)
    if not row:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    cat_rows = execute_query("""
        SELECT c.id, c.name FROM categories c
        JOIN event_categories ec ON c.id = ec.category_id
        WHERE ec.event_id = ?
    """, (event_id,))
    categories = [Category(id=cat["id"], name=cat["name"]) for cat in cat_rows]
    return Event(
        id=row["id"],
        name=row["name"],
        description=row["description"],
        start_dt=datetime.fromisoformat(row["start_dt"]),
        end_dt=datetime.fromisoformat(row["end_dt"]),
        rrule=row["rrule"],
        ha_user_id=row["ha_user_id"],
        status=row["status"],
        categories=categories
    )

@app.post("/events/create", status_code=201)
def create_event(event: Event):
    execute_query("""
        INSERT INTO events (name, description, start_dt, end_dt, rrule, ha_user_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (event.name, event.description, event.start_dt.isoformat(), event.end_dt.isoformat(), event.rrule, event.ha_user_id, event.status), commit=True)
    event_id = execute_query("SELECT last_insert_rowid()", fetchone=True)[0]
    for category in event.categories:
        if category.id:
            execute_query("INSERT INTO event_categories (event_id, category_id) VALUES (?, ?)", (event_id, category.id), commit=True)
    return {"message": "Event created successfully", "id": event_id}

@app.put("/events/{event_id}")
def update_event(event_id: int, event: Event):
    existing = execute_query("SELECT * FROM events WHERE id = ?", (event_id,), fetchone=True)
    if not existing:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    execute_query("""
        UPDATE events SET name=?, description=?, start_dt=?, end_dt=?, rrule=?, ha_user_id=?, status=? WHERE id=?
    """, (event.name, event.description, event.start_dt.isoformat(), event.end_dt.isoformat(), event.rrule, event.ha_user_id, event.status, event_id), commit=True)
    execute_query("DELETE FROM event_categories WHERE event_id=?", (event_id,), commit=True)
    for category in event.categories:
        if category.id:
            execute_query("INSERT INTO event_categories (event_id, category_id) VALUES (?, ?)", (event_id, category.id), commit=True)
    return {"message": "Event updated successfully"}

@app.delete("/events/{event_id}")
def delete_event(event_id: int):
    existing = execute_query("SELECT * FROM events WHERE id = ?", (event_id,), fetchone=True)
    if not existing:
        raise HTTPException(status_code=404, detail="NOT_FOUND")
    execute_query("DELETE FROM event_categories WHERE event_id = ?", (event_id,), commit=True)
    execute_query("DELETE FROM events WHERE id = ?", (event_id,), commit=True)
    return {"message": "Event deleted successfully"}

@app.get("/categories", response_model=List[Category])
def get_categories():
    rows = execute_query("SELECT * FROM categories")
    return [Category(id=row["id"], name=row["name"]) for row in rows]

@app.post("/categories", status_code=201)
def create_category(category: Category):
    execute_query("INSERT INTO categories (name) VALUES (?)", (category.name,), commit=True)
    category_id = execute_query("SELECT last_insert_rowid()", fetchone=True)[0]
    return {"message": "Category created successfully", "id": category_id}
