from flask import Flask, redirect, url_for, render_template, request, session
from email_validator import validate_email, EmailNotValidError
from bs4 import BeautifulSoup
from datetime import datetime
from cs50 import SQL
import requests
import hashlib
import os.path

app = Flask(__name__)
app.secret_key = "!G('ZxILCy[wX10i$2g(U>BgI*xkxL"

db = SQL("sqlite:///users.db")

errorStr = ""

articles = {}


class Register:
    def __init__(self, email, password, name, surname):
        self.email = email
        self.password = password
        self.name = name
        self.surname = surname

    def verifyEmail(self):
        try:
            validation = validate_email(self.email)
            self.email = validation.email

            return True
        except EmailNotValidError as e:
            global errorStr
            errorStr = e
            return False


def createSession(user_id, email, name, surname):
    session["user_id"] = user_id
    session["email"] = email
    session["name"] = name
    session["surname"] = surname


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("index.html", dev=False)


@app.route("/devRoute", methods=["POST"])
def devRoute():
    user_db = db.execute("SELECT * FROM users WHERE email= ?", ("dev@gmail.com"))[0]
    createSession(user_db["id"], user_db["email"], user_db["name"], user_db["surname"])
    return redirect(url_for("main"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password_hash = hashlib.sha256(request.form["password"].encode('utf-8')).hexdigest()
        newUser = Register(request.form["email"], password_hash, request.form["name"], request.form["surname"])

        if newUser.verifyEmail() == True:
            try:    #check for duplicate email
                db.execute("SELECT * FROM users WHERE email= ?", (newUser.email))[0]["email"]
                return render_template("failure.html", error="E-pasts jau izmantots!", returnPage="index")
            except:
                db.execute("INSERT INTO users (email, password, name, surname, reg_time) VALUES(?, ?, ?, ?, ?)", newUser.email, newUser.password, newUser.name, newUser.surname, datetime.now())
                user_db = db.execute("SELECT * FROM users WHERE email= ?", (newUser.email))[0]
                createSession(user_db["id"], user_db["email"], user_db["name"], user_db["surname"])

                return redirect(url_for("main"))
        else:
            del newUser
            return render_template("failure.html", error=errorStr, returnPage="index")
    else:
        return render_template("index.html")


@app.route("/gotologin", methods=["GET", "POST"])
def gotologin():
    return render_template("login.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    try:
        user_db = db.execute("SELECT * FROM users WHERE email= ?", (request.form["email"]))[0]
        password_hash = hashlib.sha256(request.form["password"].encode('utf-8')).hexdigest()
        if request.form["email"] == user_db["email"] and password_hash == user_db["password"]:
            createSession(user_db["id"], user_db["email"], user_db["name"], user_db["surname"])
            return redirect(url_for("main"))
        else:
            return render_template("failure.html", error="E-pasts vai parole nepareiza!", returnPage="login")
    except:
        return render_template("failure.html", error="E-pasts vai parole nepareiza!", returnPage="login")


@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.pop("user_id", None)
    session.pop("email", None)
    session.pop("name", None)
    session.pop("surname", None)
    return redirect(url_for("home"))


@app.route("/main", methods=["GET", "POST"])
def main():
    articles = db.execute("SELECT a.id, url, title, title_display FROM users u JOIN save s ON u.id = s.user_id JOIN articles a ON a.id = s.article_id WHERE u.email= ?", session["email"])
    for article in articles:
        article["addRoute"] = os.path.join("/inspectArticle", str(article["id"]))
        article["removeRoute"] = os.path.join("/removeArticle", str(article["id"]))
    return render_template("main.html", articles=articles, url="url", name=session["name"], surname=session["surname"])


@app.route("/addArticle", methods=["GET", "POST"])
def addArticle():
    try:
        print(request.form["addArticle"], "\n")
        get = requests.get(request.form["addArticle"])

        if get.status_code == 200 and "wiki" in request.form["addArticle"]:
            soup = BeautifulSoup(get.text, 'html.parser')

            for title in soup.find_all('title'):
                article_head = title.get_text()

            article_head = article_head.replace(" - Wikipedia", "")

            db.execute("INSERT INTO articles (url, reg_time, title, title_display) VALUES(?, ?, ?, ?)", request.form["addArticle"], datetime.now(), article_head.replace(" ", ""), article_head) #insert new article values
            article_db = db.execute("SELECT * FROM articles WHERE url= ? AND reg_time= ?", request.form["addArticle"], datetime.now())[0]
            db.execute("INSERT INTO save (user_id, article_id) VALUES(?, ?)", session["user_id"], article_db["id"])

            return redirect(url_for("main"))
        else:
            print("error")
            return redirect(url_for("main"))
    except:
        print("Request failed \n")
        return redirect(url_for("main"))

@app.route("/addNote/<article_id>", methods=["GET", "POST"])
def addNote(article_id):
    db.execute("UPDATE articles SET user_note=? WHERE id=?", request.form["note"], article_id)

    return redirect(url_for("inspectArticle", article_id=article_id))

@app.route("/inspectArticle/<article_id>", methods=["GET", "POST"])
def inspectArticle(article_id):
    try:
        article_db = db.execute("SELECT * FROM articles WHERE id= ?", article_id)[0]
        article_db["noteRoute"] = os.path.join("/addNote", str(article_db["id"]))

        title = article_db["title_display"]

        getUrl = requests.get(article_db["url"])
        soup = BeautifulSoup(getUrl.text, 'html.parser')

        links = {}
        for paragraph in soup.find_all('p'):
            for link in paragraph.find_all('a'):
                if "cite_note" not in link.get('href'):
                    if "https" not in link.get('href'):
                        path = str(article_db["url"]).replace(str(article_db["url"]).split("/")[3], "") + link.get('href')
                        links[path] = link.text
                        print(str(article_db["url"]).split("/"))
                    else:
                        links[link.get('href')] = link.text

        if article_db["user_note"] is None:
            user_note = ""
        else:
            user_note = article_db["user_note"]

        return render_template("inspect.html", title=title, links=links, user_note=user_note, noteRoute=article_db["noteRoute"])
    except:
        return redirect(url_for("main"))


@app.route("/removeArticle/<article_id>", methods=["GET", "POST"])
def removeArticle(article_id):
    db.execute("DELETE FROM save WHERE article_id=?", article_id)
    db.execute("DELETE FROM articles WHERE id=?", article_id)

    return redirect(url_for("main"))

@app.route("/user", methods=["GET", "POST"])
def user():
    if "email" in session:
        return render_template("user.html", user=session["email"], name=session["name"], surname=session["surname"])
    else:
        return redirect(url_for("home"))