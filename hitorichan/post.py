from flask import (
  Blueprint, redirect, render_template, url_for, request
)

from hitorichan.db import get_db
from datetime import datetime

bp = Blueprint("post", __name__)

@bp.route("/", methods=["GET", "POST"])
def post():
  db = get_db()
  
  if request.method == "POST":
    name = request.form["name"]
    text = request.form["text"]
    error = None
    
    if not text:
      error = "Comment is required."
    
    if name == "":
      name = "Anonymous"
    
    if error is not None:
      flash(error)
    else:
      db.execute(
        "INSERT INTO replies (name, text)"
        " VALUES (?, ?)",
        (name, text)
      )
      db.commit()
      
      return redirect(url_for("post"))
  
  replies = db.execute(
    "SELECT id, created, name, text FROM replies ORDER BY id ASC"
  ).fetchall()
  
  return render_template("post/post.html", replies=replies)
