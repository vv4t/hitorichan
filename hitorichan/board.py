from flask import (
  Blueprint, redirect, render_template, url_for, request, flash, abort
)

from hitorichan.db import get_db
from datetime import datetime

MAX_REPLIES = 500
MAX_THREADS = 50

bp = Blueprint("board", __name__, url_prefix="/1/")

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
      
      cursor.execute(
        "INSERT INTO replies (name, text, thread_id)"
        " VALUES (?, ?, ?)",
        (name, text, thread_id)
      )
      
      reply_id = cursor.lastrowid
      
      db.commit()
      
      thread_count = db.execute("SELECT Count(id) FROM threads").fetchone()[0]
      if thread_count > MAX_THREADS:
        prune_thread = db.execute(
          "SELECT thread.id"
          " FROM threads thread"
          " ORDER BY ("
          "  SELECT reply.created"
          "  FROM replies reply"
          "  WHERE reply.thread_id=thread.id"
          "  ORDER BY reply.created DESC"
          "  LIMIT 1"
          " ) ASC"
          " LIMIT 1"
        ).fetchone()
        
        thread_id = prune_thread["id"]
        
        db.execute(
          "DELETE FROM replies"
          " WHERE thread_id=?",
          (thread_id,)
        )
        
        db.execute(
          "DELETE FROM threads"
          " WHERE id=?",
          (thread_id,)
        )
        
        db.commit()
    
    return redirect(url_for("board.thread", reply_id=reply_id))
  
  threads = db.execute(
    "SELECT thread.id, thread.subject"
    " FROM threads thread"
    " ORDER BY ("
    "  SELECT reply.created"
    "  FROM replies reply"
    "  WHERE reply.thread_id=thread.id"
    "  ORDER BY reply.created DESC"
    "  LIMIT 1"
    " ) DESC"
  ).fetchall()
  
  return render_template("board.html", threads=threads, db=db)

@bp.route("/thread/<int:reply_id>", methods=["GET", "POST"])
def thread(reply_id):
  db = get_db()
  
  reply = db.execute("SELECT thread_id FROM replies WHERE id=?", (reply_id,)).fetchone()
  
  if reply is None:
    abort(404)
  
  thread_id = int(reply["thread_id"])
  reply_count = db.execute("SELECT Count(id) FROM replies WHERE thread_id=?", (thread_id,)).fetchone()[0]
  
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
      cursor = db.cursor()
      cursor.execute(
        "INSERT INTO replies (name, text, thread_id)"
        " VALUES (?, ?, ?)",
        (name, text, thread_id)
      )
      
      new_reply_id = cursor.lastrowid
      
      db.commit()
      if reply_count >= MAX_REPLIES:
        db.execute(
          "DELETE FROM replies"
          " WHERE thread_id=?",
          (thread_id,)
        )
        
        db.execute(
          "DELETE FROM threads"
          " WHERE id=?",
          (thread_id,)
        )
        
        db.commit()
        
        return redirect(url_for("board", reply_id=reply_id))
      
      return redirect(url_for("board.thread", reply_id=reply_id, _anchor="p" + str(new_reply_id)))
  
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
  
  return render_template("thread.html", thread=current_thread, replies=replies, reply_count=reply_count, MAX_REPLIES=MAX_REPLIES)
