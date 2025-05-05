from flask import Flask, request, render_template, redirect, session, flash, jsonify
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
    finally:
        conn.close()

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
    conn.close()

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

    user_id = str(session["user_id"])
    doc = firestore_db.collection("user_profiles").document(user_id).get()
    user_profile = doc.to_dict() if doc.exists else {}

    profile_complete = (
        user_profile
        and user_profile.get("interests")
        and user_profile.get("favorite_artist")
        and user_profile.get("music_genre")
    )

    # Get all user profiles for recommendation
    recommendations = []
    if profile_complete:
        current_genre = user_profile.get("music_genre", "")
        all_profiles = firestore_db.collection("user_profiles").stream()

        for profile in all_profiles:
            profile_data = profile.to_dict()
            profile_id = profile.id
            if profile_id == user_id:
                continue  # Skip current user

            # Check if profile is complete
            if not (
                profile_data.get("name")
                and profile_data.get("age")
                and profile_data.get("music_genre")
            ):
                continue  # Skip incomplete profiles

            # Calculate similarity (1 if genres match, 0 otherwise)
            similarity = 1 if profile_data.get("music_genre") == current_genre else 0
            recommendations.append({
                "name": profile_data.get("name", "未知"),
                "music_genre": profile_data.get("music_genre", "未知"),
                "favorite_artist": profile_data.get("favorite_artist", "未知"),
                "interests": profile_data.get("interests", []),
                "similarity": similarity
            })

        # Sort recommendations
        if recommendations:
            # Separate similar and non-similar users
            similar_users = [r for r in recommendations if r["similarity"] == 1]
            other_users = [r for r in recommendations if r["similarity"] == 0]
            
            # Sort similar users by name (ascending)
            similar_users.sort(key=lambda x: x["name"])
            
            # Shuffle other users for random order
            random.shuffle(other_users)
            
            # Combine lists: similar users first, then shuffled others
            recommendations = similar_users + other_users
    else:
        # If profile is incomplete, still show other complete profiles in random order
        all_profiles = firestore_db.collection("user_profiles").stream()
        for profile in all_profiles:
            profile_data = profile.to_dict()
            profile_id = profile.id
            if profile_id == user_id:
                continue  # Skip current user

            # Check if profile is complete
            if not (
                profile_data.get("name")
                and profile_data.get("age")
                and profile_data.get("music_genre")
            ):
                continue  # Skip incomplete profiles

            recommendations.append({
                "name": profile_data.get("name", "未知"),
                "music_genre": profile_data.get("music_genre", "未知"),
                "favorite_artist": profile_data.get("favorite_artist", "未知"),
                "interests": profile_data.get("interests", []),
                "similarity": 0
            })
        # Shuffle all recommendations if profile is incomplete
        random.shuffle(recommendations)

    return render_template(
        "match.html",
        user=session["user"],
        profile_complete=profile_complete,
        recommendations=recommendations
    )
# Information page
@app.route("/info")
def info():
    if "user" not in session:
        return redirect("/login")
    return render_template("info.html")

# Save music interests to Firestore
@app.route("/save_interests", methods=["POST"])
def save_interests():
    if "user_id" not in session:
        return jsonify({"error": "未登入"}), 401
    
    data = request.get_json()
    if not data or not data.get("name") or not data.get("age") or not data.get("music_genre"):
        return jsonify({"error": "缺少姓名、年齡或音樂類型"}), 400

    try:
        age = int(data.get("age"))
        if age <= 0:
            return jsonify({"error": "年齡無效"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "年齡必須為數字"}), 400

    firestore_db.collection("user_profiles").document(str(session["user_id"])).set({
        "name": data.get("name"),
        "age": age,
        "interests": data.get("interests") or [],
        "favorite_artist": data.get("favorite_artist") or "",
        "music_genre": data.get("music_genre") or ""
    })
    return jsonify({"status": "success"}), 200

# Logout
@app.route("/logout")
def logout():
    session.clear()
    flash("已成功登出")
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)