from flask import (
  Blueprint, render_template, url_for
)

from datetime import datetime

bp = Blueprint("thread", __name__)

@bp.route("/")
def index():
  posts = [
    { "time": datetime.now(), "id": 1, "text": "OK" },
    { "time": datetime.now(), "id": 2, "text": "Epic sugoi" },
    { "time": datetime.now(), "id": 3, "text": "nice very cool" },
  ]
  
  return render_template("thread/index.html", posts=posts)
