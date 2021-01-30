import os
from flask import Flask, render_template
from flask_pymongo import PyMongo
if os.path.exists("env.py"):
    import env

app = Flask(__name__)


@app.route("/")
@app.route("/index.html")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=os.environ.get("PORT"),
            debug=True)
