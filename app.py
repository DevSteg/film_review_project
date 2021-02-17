import os
from flask import (
    Flask, render_template, url_for,
    flash, redirect, request, session)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import (
    generate_password_hash, check_password_hash)
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/index")
def index():
    films = mongo.db.films.find()
    return render_template("index.html", films=films)


@app.route("/films")
def films():
    films = mongo.db.films.find()
    return render_template("films.html", films=films)


@app.route("/films/<film_id>")
def movie(film_id):
    movie = mongo.db.films.find_one(
        {"_id": ObjectId(film_id)})
    return render_template("movie.html", movie=movie)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("search")
    films = mongo.db.films.find({"$text": {"$search": query}})
    return render_template("films.html", films=films)


@app.route("/add_film", methods=["GET", "POST"])
def add_film():
    if request.method == "POST":
        # Check if film already exists
        existing_film = mongo.db.films.find_one({
            "film_title": request.form.get("film_title").lower(),
            "release_date": request.form.get("release_date")
        })

        # If film exists redirect to the films page
        if existing_film:
            flash("Film already exists!")
            return redirect(url_for(
                "movie", film_id=existing_film["_id"]))

        # If the film does not exist in the db
        new_film = {
            "film_img": request.form.get("film_img"),
            "film_title": request.form.get("film_title").lower(),
            "genre": request.form.get("genre").lower(),
            "release_date": request.form.get("release_date"),
            "desc": request.form.get("desc").lower(),
            "created_by": session["user"]
        }

        mongo.db.films.insert_one(new_film)
        flash("Film successfully added!")
        return redirect(url_for("movie", film_id=new_film["_id"]))

    return render_template("add_film.html")


@app.route("/review/<film_id>", methods=["GET", "POST"])
def review(film_id):

    if session:
        film = mongo.db.films.find_one(
            {"_id": ObjectId(film_id)})

        if request.method == "POST":
            review = {
                "film_id": film["_id"],
                "film_title": film["film_title"],
                "review": request.form.get("review"),
                "created_by": session["user"]
            }

            mongo.db.reviews.insert_one(review)
            flash("Review Added")
            return redirect(url_for("movie", film_id=film["_id"]))

        return render_template("review.html", film=film)

    flash("You must login/Register to leave a review")
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # first check is username exists
        existing_user = mongo.db.users.find_one({
            "username": request.form.get("username").lower()
        })

        if existing_user:
            flash("User already exists")
            return redirect(url_for("register"))

        # if user does not exists register new user
        register_user = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }

        mongo.db.users.insert_one(register_user)

        session["user"] = request.form.get("username").lower()
        flash("Registration Successful")
        return redirect(url_for(
                        "profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if username exists
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # If user exists check the password is correct
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username").lower()
                    flash("Login Successful")
                    return redirect(url_for(
                        "profile", username=session["user"]))

            else:
                # Incorrect Password
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # Incorrect Username
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    email = mongo.db.users.find_one(
        {"username": session["user"]})["email"]

    if session["user"]:
        return render_template(
            "profile.html", username=username, email=email)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    flash("You have been successfully logged out!")
    session.pop("user")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=os.environ.get("PORT"),
            debug=True)
