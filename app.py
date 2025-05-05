from flask import Flask, request, render_template, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "your-secret-key"

# Initialize SQLite
def get_db():
    conn = sqlite3.connect("models.db")
    conn.row_factory = sqlite3.Row
    return conn

# Initialize Firebase
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
firestore_db = firestore.client()

# Home page
@app.route("/")
def index():
    return render_template("index.html")

# Register page
@app.route("/register")
def show_register():
    return render_template("register.html")

# Register action
@app.route("/signup", methods=["POST"])
def signup():
    name = request.form["name"]
    email = request.form["email"]
    password = generate_password_hash(request.form["password"])

    conn = get_db()
    try:
        conn.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        flash("註冊成功！請登入")
        return redirect("/login")
    except sqlite3.IntegrityError:
        flash("Email 已被註冊")
        return redirect("/register")

# Login page
@app.route("/login")
def show_login():
    return render_template("login.html")

# Login action
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user["password"], password):
        session["user"] = user["name"]
        session["user_id"] = user["id"]
        flash("登入成功，歡迎 " + user["name"])
        return redirect("/match")
    else:
        flash("登入失敗，請檢查帳密")
        return redirect("/login")

# Match page
@app.route("/match")
def match():
    if "user" not in session:
        return redirect("/login")
    return render_template("match.html", user=session["user"])

# Save music interests to Firestore
@app.route("/save_interests", methods=["POST"])
def save_interests():
    if "user_id" not in session:
        return redirect("/login")
    interests = request.form.getlist("interests")
    firestore_db.collection("user_profiles").document(str(session["user_id"])).set({
        "interests": interests
    })
    flash("興趣儲存成功！")
    return redirect("/match")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("已成功登出")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)