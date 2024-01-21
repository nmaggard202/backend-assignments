import json
from flask import Flask, request
import db
import hashlib
import os

DB = db.DatabaseDriver()
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


@app.route("/api/transactions/", methods=["POST"])
def create_transaction():
    """Endpoint for creating a transaction"""
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    message = body.get("message")
    accepted = body.get("accepted", None)
    transaction_id = DB.insert_transaction_table(
        sender_id, receiver_id, amount, message, accepted
    )
    transaction = DB.get_transaction_by_id(transaction_id)
    if transaction is None:
        return json.dumps({"error": "Creating this transaction did not work!"}), 400
    return json.dumps(transaction), 200


@app.route("/api/transactions/<int:transaction_id>/", methods=["POST"])
def update_transaction(transaction_id):
    """Endpoint for updating a transaction"""
    body = json.loads(request.data)
    accepted = body.get("accepted")
    transaction = DB.get_transaction_by_id(transaction_id)
    sender_id = transaction.get("sender_id")
    receiver_id = transaction.get("receiver_id")
    amount = transaction.get("amount")
    if transaction is None:
        return json.dumps({"error": "Creating this transaction did not work!"}), 400
    current_status = transaction.get("accepted")
    if current_status == None and accepted == "true":
        DB.update_transaction_by_id(transaction_id, accepted)
        DB.update_balances_by_id(sender_id, receiver_id, amount)
    if current_status == None and accepted == "false":
        DB.update_transaction_by_id(transaction_id, "false")
    if current_status == "true" or current_status == "false":
        return json.dumps({"Forbidden": "Can not edit this transaction."}), 403
    return json.dumps(transaction), 200


# Tier 1 - Friendships


@app.route("/api/extra/users/<int:user_id>/friends/")
def get_friends(user_id):
    """Endpoint for getting a user's friends by ID"""
    friends = DB.get_friendships_by_id(user_id)
    return {"friends": friends}, 200


@app.route("/api/extra/users/<int:user_id>/friends/<int:friend_id>/", methods=["POST"])
def create_friendship(user_id, friend_id):
    """Endpoint for creating a friendship"""
    DB.insert_friendships_table(user_id, friend_id)
    return json.dumps("Success"), 201


# Tier 2 - Join


@app.route("/api/extra/users/<int:user_id>/join/")
def get_txns_by_user(user_id):
    """Endpoint for getting a user's friends by ID"""
    transactions = DB.get_transactions_by_user(user_id)
    return {"transactions": transactions}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
