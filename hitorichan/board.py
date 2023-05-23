from flask import (
  Blueprint, redirect, render_template, url_for, request, flash
)

from hitorichan.db import get_db
from datetime import datetime

bp = Blueprint("board", __name__)

@bp.route("/", methods=["GET", "POST"])
def board():
  db = get_db()
  
  if request.method == "POST":
    name = request.form["name"]
    subject = request.form["subject"]
    text = request.form["text"]
    error = None
    
    if not text:
      error = "Comment is required."
    
    if name == "":
      name = "Anonymous"
    
    if error is not None:
      flash(error)
    else:
      cursor = db.cursor()
      cursor.execute(
        "INSERT INTO threads (subject)"
        " VALUES (?)",
        (subject,)
      )
      
      thread_id = cursor.lastrowid
      
      db.execute(
        "INSERT INTO replies (name, text, thread_id)"
        " VALUES (?, ?, ?)",
        (name, text, thread_id)
      )
      
      db.commit()
    
    return redirect(url_for("board.board"))
  
  threads = db.execute(
    "SELECT id, subject FROM threads"
  ).fetchall()
  
  return render_template("board.html", threads=threads, db=db)

@bp.route("/thread/<int:reply_id>", methods=["GET", "POST"])
def thread(reply_id):
  db = get_db()
  
  reply = db.execute("SELECT thread_id FROM replies WHERE id=?", (reply_id,)).fetchone()
  thread_id = int(reply["thread_id"])
  
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
        "INSERT INTO replies (name, text, thread_id)"
        " VALUES (?, ?, ?)",
        (name, text, thread_id)
      )
      db.commit()
    
    return redirect(url_for("board.thread", reply_id=reply_id))
  
  current_thread = db.execute(
    "SELECT * FROM threads WHERE id=?",
    (thread_id,)
  ).fetchone()
  
  replies = db.execute(
    "SELECT id, created, name, text FROM replies"
    " WHERE thread_id=?"
    " ORDER BY id ASC",
    (thread_id,)
  ).fetchall()
  
  if replies[0]["id"] != reply_id:
    return redirect(url_for("board.thread", reply_id=replies[0]["id"], _anchor="p" + str(reply_id)))
  
  return render_template("thread.html", thread=current_thread, replies=replies)
