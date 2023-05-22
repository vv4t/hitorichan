from flask import (
  Blueprint, render_template, url_for, request
)

from datetime import datetime

bp = Blueprint("post", __name__)

replies = [
  { "time": datetime.now(), "name": "Anonymous", "id": 1, "text": "OK" },
  { "time": datetime.now(), "name": "Anonymous", "id": 2, "text": "Epic sugoi" },
  { "time": datetime.now(), "name": "Anonymous", "id": 3, "text": "nice very cool" },
]

@bp.route("/", methods=["GET", "POST"])
def post():
  if request.method == "POST":
    name = request.form["name"]
    
    if name == "":
      name = "Anonymous"
    
    reply =  {
      "name": name,
      "time": datetime.now(),
      "id": replies[-1]["id"] + 1,
      "text": request.form["text"]
    }
    
    replies.append(reply)
  
  return render_template("post/post.html", replies=replies)
