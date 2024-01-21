import os
import sqlite3


# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        """
        Secure a connection with the database and stores it into the instance variable 'conn'
        """
        self.conn = sqlite3.connect("users.db", check_same_thread=False)
        self.create_user_table()

    def create_user_table(self):
        """
        Using SQL, creates a users table.
        """
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL,
            balance INTEGER,
            password TEXT
            );"""
        )

    def delete_user_table(self):
        """
        Using SQL, deletes a user table
        """
        self.conn.execute("""DROP TABLE IF EXISTS user""")

    def get_all_users(self):
        """
        Using SQL, returns all users in a table
        """
        cursor = self.conn.execute("SELECT * FROM user")
        users = []
        for row in cursor:
            users.append({"id": row[0], "name": row[1], "username": row[2]})
        return users

    def get_user_by_id(self, id):
        """
        Using SQL, returns a task by id
        """
        cursor = self.conn.execute("SELECT * FROM user WHERE id = ?;", (id,))
        for row in cursor:
            return {"id": row[0], "name": row[1], "username": row[2], "balance": row[3]}
        return None

    def insert_user_table(self, name, username, balance):
        """
        Using SQL, inserts a task into the task table
        """
        cursor = self.conn.execute(
            "INSERT INTO user(name, username, balance) VALUES (?, ?, ?);",
            (name, username, balance),
        )
        self.conn.commit()
        return cursor.lastrowid

    def delete_user_by_id(self, id):
        """
        Using SQL, deletes a user from a table
        """
        self.conn.execute("DELETE FROM user WHERE id = ?;", (id,))
        self.conn.commit()

    def update_balances_by_id(self, sender_id, receiver_id, amount):
        """
        Using SQL, updates a user in the table
        """
        sender_user = self.get_user_by_id(sender_id)
        sender_balance = sender_user["balance"] - amount

        receiver_user = self.get_user_by_id(receiver_id)
        receiver_balance = receiver_user["balance"] + amount

        self.conn.execute(
            "UPDATE user SET balance = ? WHERE id = ?;",
            (sender_balance, sender_id),
        )
        self.conn.execute(
            "UPDATE user SET balance = ? WHERE id = ?;",
            (receiver_balance, receiver_id),
        )

        self.conn.commit()

    # Extra Credit

    def insert_user_table_protected(self, name, username, balance, password):
        """
        Using SQL, inserts a user into the user table
        """
        cursor = self.conn.execute(
            "INSERT INTO user(name, username, balance, password) VALUES (?, ?, ?, ?);",
            (name, username, balance, password),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_user_password(self, id):
        """
        Do this.
        """
        cursor = self.conn.execute("SELECT * FROM user WHERE id = ?;", (id,))
        for row in cursor:
            return row[4]
        return None


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
