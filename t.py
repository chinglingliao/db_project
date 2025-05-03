from flask import Flask, request, render_template, redirect, session, flash
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
db.collection("123").add({"1":2})

app = Flask(__name__)
app.secret_key = "any-random-string-you-want"  # 可以是亂碼、暱稱都行


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

@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    # 查詢 Firestore 中是否有對應帳號
    users_ref = db.collection("users")
    query = users_ref.where("email", "==", email).limit(1).stream()
    user = None
    for doc in query:
        user = doc.to_dict()

    if user and user["password"] == password:
        session["user"] = user["name"]  # 紀錄登入狀態
        flash("登入成功！歡迎 " + user["name"])
        return redirect("/love")
    else:
        flash("登入失敗，帳號或密碼錯誤")
        return redirect("/login")

#配對邀請頁面
@app.route("/love")
def show_love():
    return render_template("4.html")

@app.route("/love")
def love():
    user = session.get("user")
    if not user:
        return redirect("/login")
    return f"歡迎你，{user}！這是配對頁"

@app.route("/logout")
def logout():
    session.pop("user", None)  # 移除登入資訊
    return redirect("/")

if __name__ == "__main__":
    app.run()