import os
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse
import click
from flask import current_app, g

def get_db():
  if "db" not in g:
    if os.getenv("DB_URL"):
      db_url = urlparse(os.getenv('DB_URL'))
      db_conn = psycopg2.connect(
        host=db_url.hostname,
        database=db_url.path[1:],
        user=db_url.username,
        password=db_url.password
      )
      db_conn.autocommit = True
      g.db = db_conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
  
  return g.db

def close_db(e=None):
  db = g.pop("db", None)
  
  if db is not None:
    db.close()

def init_db():
  db = get_db()
  
  with current_app.open_resource("schema.sql") as f:
    script = f.read().decode("utf-8")
    
    for cmd in (" ".join(script.replace("\n", " ").split()).split(";")[:-1]):
      db.execute(cmd.strip() + ";")

@click.command("init-db")
def init_db_command():
  init_db()
  click.echo("Initialised the database.")

def init_app(app):
  app.teardown_appcontext(close_db)
  app.cli.add_command(init_db_command)
