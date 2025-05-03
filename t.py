from flask import Flask, request, render_template, redirect
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
db.collection("123").add({"1":2})

app = Flask(__name__)

#主頁
@app.route("/")
def index():
    return render_template("1.html") 

#註冊頁面
@app.route("/showsingup")
def show_signup():
    return render_template("2.html")

#註冊功能
@app.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    email = request.form["email"]
    password = request.form["password"]

    # 儲存到 Firebase Firestore
    db.collection("users").add({
        "name": name,
        "email": email,
        "password": password
    })

    return "註冊成功！收到名字：" + name

#登入頁面
@app.route("/login")
def show_login():
    return render_template("3.html")

#配對邀請頁面
@app.route("/love")
def show_love():
    return render_template("4.html")

if __name__ == "__main__":
    app.run()