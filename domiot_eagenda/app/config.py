import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    if os.environ.get("FLASK_DEBUG") == "1":
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    else:
        # Use /data/db.sqlite3 directory for production
        SQLALCHEMY_DATABASE_URI = 'sqlite:////data/db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORE_ADDON_HOSTNAME = os.environ.get("FLASK_CORE_ADDON_HOSTNAME")