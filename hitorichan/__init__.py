import os

from flask import (
  Flask, render_template
)

def create_app(test_config=None):
  app = Flask(__name__, instance_relative_config=True)
  app.config.from_mapping(
    SECRET_KEY="dev",
    DATABASE=os.path.join(app.instance_path, "hitorichan.sqlite")
  )
  
  if test_config is None:
    app.config.from_pyfile("config.py", silent=True)
  else:
    app.config.from_mapping(test_config)
  
  try:
    os.makedirs(app.instance_path)
  except OSError:
    pass
  
  from . import db
  db.init_app(app)
  
  from . import board
  app.register_blueprint(board.bp)
  app.add_url_rule("/1/", endpoint="board")
  
  @app.route("/")
  def index():
    latest_posts = db.get_db().execute(
      "SELECT id, text FROM replies ORDER BY created LIMIT 10"
    ).fetchall()
    
    return render_template("index.html", latest_posts=latest_posts)
  
  return app
