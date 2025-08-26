from flask import Flask, redirect, session, request
from replit import db
import random, os

replit_username = "mattsalhome"

app = Flask(__name__, static_url_path="/static")
app.secret_key = os.environ['sessionKey']

db["user"] = {"username": "matt", "password": "mattias1"}

def getBlogs():
  entry = ""
  with open("entry.html", "r") as f:
      entry = f.read()

  keys = db.keys()
  keys = list(keys)
  content = ""
  for key in reversed(keys):
      if key != "user":
          thisEntry = entry
          db_entry = db[key]
          title = db_entry.get("title", "No Title")
          date = db_entry.get("date", "No Date")
          body = db_entry.get("body", "No Body")

          thisEntry = thisEntry.replace("{title}", title)
          thisEntry = thisEntry.replace("{date}", date)
          thisEntry = thisEntry.replace("{body}", body)
          content += thisEntry

  return content


@app.route("/")
def index():
  userid = request.headers['X-Replit-User-Name']
  if userid == replit_username:
    return redirect("/edit")
  page = ""
  f = open("blog.html")
  page = f.read()
  page = page.replace("{content}", getBlogs())
  f.close()
  return page

@app.route("/edit")
def edit():
  userid = request.headers['X-Replit-User-Name']
  print(userid)
  if userid != replit_username:
        return redirect("/")
  page = ""
  f = open("edit.html")
  page = f.read()
  page = page.replace("{content}", getBlogs())
  f.close()
  return page

@app.route("/add", methods=["POST"])
def add():
  userid = request.headers['X-Replit-User-Name']
  if userid != replit_username:
    return redirect("/")
  form = request.form 
  title = form["title"]
  date = form["date"]
  body = form["body"]

  entry = {"title": title, "date": date, "body": body}
  db[form["date"]] = entry
  return redirect("/edit")

@app.route("/signup")
def signup():
  if session.get('loggedIn'):
      return redirect("/edit")
  try:
      f = open("account/signup.html", "r")
      page = f.read()
      f.close()
  except FileNotFoundError:
      page = "<p>Signup page not found.</p>"
  return page

@app.route("/signup", methods=["POST"])
def create():
  if session.get('loggedIn'):
      return redirect("/edit")
  form = request.form
  username = form["username"]
  name = form["name"]
  password = form["password"]

  if username not in db:
      salt = str(random.randint(1000, 9999))
      newPassword = hash(password + salt)
      db[username] = {"name": name, "password": newPassword, "salt": salt}
      return redirect("/login")  
  else:
      return redirect("/signup")

@app.route("/login")
def login():
  userid = request.headers['X-Replit-User-Name']
  if userid == replit_username:
    return redirect("/edit")
  try:
      f = open("account/login.html", "r")
      page = f.read()
      f.close()
  except FileNotFoundError:
    page = "<p>Signup page not found.</p>"
  return page

@app.route("/login", methods=["POST"])
def logUser():
  if session.get('loggedIn'):
        return redirect("/edit")
  form = request.form
  username = form["username"]
  password = form["password"]

  if username not in db:
    return redirect("/login")

  user = db[username]
  salt = user["salt"]
  hashedPass = hash(password + salt)

  if hashedPass == user["password"]:
      session["loggedIn"] = username  
      return redirect("/edit")
  else:
    return redirect("/login")


@app.route("/logout")
def logout():
  session.clear()
  return redirect("/")

app.run(host='0.0.0.0', port=81)
