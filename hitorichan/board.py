from flask import (
  Blueprint, redirect, render_template, url_for, request, flash, abort
)

from hitorichan.db import get_db
from datetime import datetime

MAX_REPLIES = 500
MAX_THREADS = 50

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
      db.execute(
        "INSERT INTO threads (subject)"
        " VALUES (%s) RETURNING id;",
        (subject,)
      )
      
      thread_id = db.fetchone()["id"]
      
      db.execute(
        "INSERT INTO replies (name, text, thread_id)"
        " VALUES (%s, %s, %s) RETURNING id;",
        (name, text, thread_id)
      )
      
      reply_id = db.fetchone()["id"]
      
      db.execute("SELECT COUNT(id) FROM threads;")
      thread_count = db.fetchone()["count"]
      if thread_count > MAX_THREADS:
        db.execute(
          "SELECT thread.id"
          " FROM threads thread"
          " ORDER BY ("
          "  SELECT reply.created"
          "  FROM replies reply"
          "  WHERE reply.thread_id=thread.id"
          "  ORDER BY reply.created DESC"
          "  LIMIT 1"
          " ) ASC"
          " LIMIT 1;"
        )
        
        prune_id = db.fetchone()["id"]
        
        db.execute(
          "DELETE FROM replies"
          " WHERE thread_id=%s;",
          (prune_id,)
        )
        
        db.execute(
          "DELETE FROM threads"
          " WHERE id=%s",
          (prune_id,)
        )
      
      return redirect(url_for("board.thread", reply_id=reply_id))
  
  db.execute(
    "SELECT thread.id, thread.subject"
    " FROM threads thread"
    " ORDER BY ("
    "  SELECT reply.created"
    "  FROM replies reply"
    "  WHERE reply.thread_id=thread.id"
    "  ORDER BY reply.created DESC"
    "  LIMIT 1"
    " ) DESC;"
  )
  
  threads = db.fetchall()
  
  print(threads);
  
  return render_template("board.html", threads=threads, db=db)

@bp.route("/thread/<int:reply_id>", methods=["GET", "POST"])
def thread(reply_id):
  db = get_db()
  
  db.execute("SELECT thread_id FROM replies WHERE id=%s", (reply_id,))
  reply = db.fetchone()
  
  if reply is None:
    abort(404)
  
  thread_id = int(reply["thread_id"])
  
  db.execute("SELECT COUNT(id) FROM replies WHERE thread_id=%s", (thread_id,))
  reply_count = db.fetchone()["count"]
  
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
        " VALUES (%s, %s, %s) RETURNING id;",
        (name, text, thread_id)
      )
      
      new_reply_id = db.fetchone()["id"]
      
      if reply_count + 1 > MAX_REPLIES:
        db.execute(
          "DELETE FROM replies"
          " WHERE thread_id=%s;",
          (thread_id,)
        )
        
        db.execute(
          "DELETE FROM threads"
          " WHERE id=%s;",
          (thread_id,)
        )
        
        return redirect(url_for("board"))
      
      return redirect(url_for("board.thread", reply_id=reply_id, _anchor="p" + str(new_reply_id)))
  
  db.execute(
    "SELECT * FROM threads WHERE id=%s;",
    (thread_id,)
  )
  current_thread = db.fetchone()
  
  db.execute(
    "SELECT id, created, name, text FROM replies"
    " WHERE thread_id=%s"
    " ORDER BY id ASC;",
    (thread_id,)
  )
  
  replies = db.fetchall()
  
  if replies[0]["id"] != reply_id:
    return redirect(url_for("board.thread", reply_id=replies[0]["id"], _anchor="p" + str(reply_id)))
  
  return render_template("thread.html", thread=current_thread, replies=replies, reply_count=reply_count, MAX_REPLIES=MAX_REPLIES)
