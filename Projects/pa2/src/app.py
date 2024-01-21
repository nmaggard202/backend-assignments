import json
from flask import Flask, request
import db
import hashlib
import os
from dotenv import load_dotenv

DB = db.DatabaseDriver()
load_dotenv()
app = Flask(__name__)


@app.route("/")
@app.route("/api/users/")
def get_users():
    """Endpoint for getting all users"""
    return json.dumps({"users": DB.get_all_users()}), 200


@app.route("/api/users/", methods=["POST"])
def create_user():
    """Endpoint for creating a user"""
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)
    user_id = DB.insert_user_table(name, username, balance)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "Creating this user did not work!"}), 400
    return json.dumps(user), 200


@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """Endpoint for getting a user by ID"""
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found!"}), 404
    return json.dumps(user), 200


@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user_by_id(user_id):
    """Endpoint for deleting a user"""
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found"}), 404
    DB.delete_user_by_id(user_id)
    return json.dumps(user), 200


@app.route("/api/send/", methods=["POST"])
def send_money():
    """Endpoint for updating a task"""
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    DB.update_balances_by_id(sender_id, receiver_id, amount)
    return (
        json.dumps(
            {"sender_id": sender_id, "receiver_id": receiver_id, "amount": amount}
        ),
        200,
    )


# Extra Credit

salt = os.environ.get("PASSWORD_SALT").encode("utf-8")
iter = int(os.environ.get("NUMBER_OF_ITERATIONS"))


@app.route("/api/extra/users/", methods=["POST"])
def create_user_protected():
    """Endpoint for creating a user"""
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)
    password = hashlib.pbkdf2_hmac(
        "sha256", body.get("password").encode("utf-8"), salt, iter, dklen=None
    ).hex()
    user_id = DB.insert_user_table_protected(name, username, balance, password)
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "Creating this user did not work!"}), 400
    return json.dumps(user), 200


@app.route("/api/extra/users/<int:user_id>/")
def get_user_protected(user_id):
    """Endpoint for getting a user by ID"""
    user = DB.get_user_by_id(user_id)
    if user is None:
        return json.dumps({"error": "User not found!"}), 404
    try:
        body = json.loads(request.data)
    except:
        return json.dumps({"error": "Unauthorized"}), 401
    password = hashlib.pbkdf2_hmac(
        "sha256",
        json.loads(request.data).get("password").encode("utf-8"),
        salt,
        iter,
        dklen=None,
    ).hex()
    if DB.get_user_password(user_id) != password:
        return json.dumps({"error": "Unauthorized"}), 401
    return json.dumps(user), 200


@app.route("/api/extra/send/", methods=["POST"])
def send_money_protected():
    """Endpoint for updating a task"""
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    password = hashlib.pbkdf2_hmac(
        "sha256",
        body.get("password").encode("utf-8"),
        salt,
        iter,
        dklen=None,
    ).hex()
    if DB.get_user_password(sender_id) != password:
        return json.dumps({"error": "Unauthorized"}), 401
    DB.update_balances_by_id(sender_id, receiver_id, amount)
    return (
        json.dumps(
            {"sender_id": sender_id, "receiver_id": receiver_id, "amount": amount}
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
