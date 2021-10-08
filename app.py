import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/home_page")
def home_page():
    return render_template("index.html")


@app.route("/")
@app.route("/get_lyrics")
def get_lyrics():
    lyric = list(mongo.db.lyrics.find())
    return render_template("lyrics.html", lyric=lyric)


@app.route("/search", methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    lyric = list(mongo.db.lyrics.find({"$text": {"$search": query}}))
    return render_template("lyrics.html", lyric=lyric)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration Successful!")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # check if username exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # ensure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        session["user"] = request.form.get("username").lower()
                        flash("Welcome, {}".format(
                            request.form.get("username")))
                        return redirect(url_for(
                            "profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))

        else:
            # username doesn't exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # grab the session user's username from db
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        return render_template("profile.html", username=username)

    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookie
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login"))


@app.route("/add_lyrics", methods=["GET", "POST"])
def add_lyrics():
    if request.method == "POST":
        lyrics = {
            "music_genre": request.form.get("music_genre"),
            "artist_name": request.form.get("artist_name"),
            "song_title": request.form.get("song_title"),
            "song_lyrics": request.form.get("song_lyrics"),
            "song_composer": request.form.get("song_composer"),
            "image_url": request.form.get("image_url"),
            "created_by": session["user"]
        }
        mongo.db.lyrics.insert_one(lyrics)
        flash("Lyrics Sucessfully Added")
        return redirect(url_for("get_lyrics"))

    genre = mongo.db.genre.find().sort("music_genre", 1)
    return render_template("add_lyrics.html", genre=genre)


@app.route("/edit_lyrics/<lyrics_id>", methods=["GET", "POST"])
def edit_lyrics(lyrics_id):
    if request.method == "POST":
        submit = {
            "music_genre": request.form.get("music_genre"),
            "artist_name": request.form.get("artist_name"),
            "song_title": request.form.get("song_title"),
            "song_lyrics": request.form.get("song_lyrics"),
            "song_composer": request.form.get("song_composer"),
            "image_url": request.form.get("image_"),
            "created_by": session["user"]
        }
        mongo.db.lyrics.update({"_id": ObjectId(lyrics_id)}, submit)
        flash("Lyrics Sucessfully Updated")

    lyric = mongo.db.lyrics.find_one({"_id": ObjectId(lyrics_id)})
    genre = mongo.db.genre.find().sort("music_genre", 1)
    return render_template("edit_lyrics.html", lyric=lyric, genre=genre)


@app.route("/delete_lyrics/<lyrics_id>")
def delete_lyrics(lyrics_id):
    mongo.db.lyrics.remove({"_id": ObjectId(lyrics_id)})
    flash("Lyrics Successfully Deleted")
    return redirect(url_for("get_lyrics"))


@app.route("/get_genres")
def get_genres():
    genre = list(mongo.db.genre.find().sort("music_genre", 1))
    return render_template("genres.html", genre=genre)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
