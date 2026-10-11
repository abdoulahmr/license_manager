import sqlite3
from flask import g, current_app

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(current_app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app):
    app.teardown_appcontext(close_db)
    with app.app_context():
        db = get_db()
        schema_path = app.config['SCHEMA_PATH']
        with open(schema_path) as f:
            db.executescript(f.read())
        db.commit()
        print(f'[init_db] schema applied -> {app.config["DATABASE"]}')

def query(sql, args=(), one=False):
    cur = get_db().execute(sql, args)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows

def execute(sql, args=(), commit=True):
    db = get_db()
    cur = db.execute(sql, args)
    last_id = cur.lastrowid
    cur.close()
    if commit:
        db.commit()
    return last_id