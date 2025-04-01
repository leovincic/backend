from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Connect to MongoDB (Replace with your Railway MongoDB URL)
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://your_mongo_url")
client = MongoClient(MONGO_URI)
db = client["webos"]  # Database name
users_collection = db["users"]  # Collection for users
passwords_collection = db["passwords"]  # Collection for password manager

# ==================== USER SIGNUP ====================
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    profile_photo = data.get("profile_photo", "")  # Optional profile photo

    if users_collection.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400

    users_collection.insert_one({"username": username, "password": password, "profile_photo": profile_photo})
    return jsonify({"message": "Signup successful!"}), 201

# ==================== USER LOGIN ====================
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return jsonify({"message": "Login successful!", "profile_photo": user.get("profile_photo", "")}), 200
    return jsonify({"error": "Invalid credentials"}), 401

# ==================== PASSWORD MANAGER ====================
@app.route("/save-password", methods=["POST"])
def save_password():
    data = request.json
    username = data.get("username")
    site = data.get("site")
    site_password = data.get("password")

    if not username or not site or not site_password:
        return jsonify({"error": "Missing data"}), 400

    passwords_collection.insert_one({"username": username, "site": site, "password": site_password})
    return jsonify({"message": "Password saved!"}), 201

@app.route("/get-passwords", methods=["GET"])
def get_passwords():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username required"}), 400

    passwords = list(passwords_collection.find({"username": username}, {"_id": 0, "username": 0}))
    return jsonify(passwords), 200

# ==================== RUN SERVER ====================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
