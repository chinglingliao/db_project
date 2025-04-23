import firebase_admin, flask
from flask import Flask, render_template
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
db.collection("123").add({"1":2})

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("1.html")

@app.route("/1")
def indexx():
    return render_template("2.html")

if __name__ == "__main__":
    app.run()