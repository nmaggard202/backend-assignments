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
        self.create_transactions_table()
        self.create_friendships_table()

    def create_user_table(self):
        """
        Using SQL, creates a users table.
        """
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS user(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL,
            balance INTEGER
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
        transactions = []
        cursor1 = self.conn.execute(
            "SELECT * FROM transactions WHERE sender_id = ?;", (id,)
        )
        for row in cursor1:
            transactions.append(
                {
                    "sender_id": row[2],
                    "receiver_id": row[3],
                    "amount": row[4],
                    "message": row[5],
                    "accepted": row[6],
                }
            )
        cursor2 = self.conn.execute(
            "SELECT * FROM transactions WHERE receiver_id = ?;", (id,)
        )
        for row in cursor2:
            transactions.append(
                {
                    "sender_id": row[2],
                    "receiver_id": row[3],
                    "amount": row[4],
                    "message": row[5],
                    "accepted": row[6],
                }
            )
        cursor3 = self.conn.execute("SELECT * FROM user WHERE id = ?;", (id,))
        for row in cursor3:
            return {
                "id": row[0],
                "name": row[1],
                "username": row[2],
                "balance": row[3],
                "transactions": transactions,
            }
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

    def create_transactions_table(self):
        """
        Using SQL, creates a transactions table.
        """
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            amount INTEGER NOT NULL,
            message TEXT NOT NULL,
            accepted TEXT,
            FOREIGN KEY(sender_id) REFERENCES user(id),
            FOREIGN KEY(receiver_id) REFERENCES user(id)
            );"""
        )

    def delete_transactions_table(self):
        """
        Using SQL, deletes a transactions table
        """
        self.conn.execute("""DROP TABLE IF EXISTS transactions""")

    def insert_transaction_table(
        self, sender_id, receiver_id, amount, message, accepted=None
    ):
        """
        Using SQL, inserts a transaction into the transactions table
        """
        cursor = self.conn.execute(
            "INSERT INTO transactions(sender_id, receiver_id, amount, message, accepted) VALUES (?, ?, ?, ?, ?);",
            (sender_id, receiver_id, amount, message, accepted),
        )
        if accepted == "true":
            self.update_balances_by_id(sender_id, receiver_id, amount)
        self.conn.commit()
        return cursor.lastrowid

    def get_transaction_by_id(self, id):
        """
        Using SQL, returns a transaction by id
        """
        cursor = self.conn.execute("SELECT * FROM transactions WHERE id = ?;", (id,))
        for row in cursor:
            return {
                "id": row[0],
                "timestamp": row[1],
                "sender_id": row[2],
                "receiver_id": row[3],
                "amount": row[4],
                "message": row[5],
                "accepted": row[6],
            }
        return None

    def update_transaction_by_id(self, id, status):
        """
        Using SQL, updates a transaction in the table
        """
        self.conn.execute(
            "UPDATE transactions SET accepted = ? WHERE id = ?;",
            (status, id),
        )

        self.conn.commit()

    # Tier 1 - Friendships

    def create_friendships_table(self):
        """
        Using SQL, creates a friendships table.
        """
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS friendships(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            friend_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES user(id),
            FOREIGN KEY(friend_id) REFERENCES user(id)
            );"""
        )

    def delete_friendships_table(self):
        """
        Using SQL, deletes a friendships table
        """
        self.conn.execute("""DROP TABLE IF EXISTS friendships""")

    def insert_friendships_table(self, user_id, friend_id):
        """
        Using SQL, inserts a friendship into the friendships table
        """
        cursor = self.conn.execute(
            "INSERT INTO friendships(user_id, friend_id) VALUES (?, ?);",
            (user_id, friend_id),
        )
        self.conn.commit()

    def get_friendships_by_id(self, user_id):
        """
        Using SQL, returns a friendship by user id
        """
        cursor = self.conn.execute(
            "SELECT * FROM friendships WHERE user_id = ?;", (user_id,)
        )
        friends = []
        for row in cursor:
            friends.append(row[2])
        friends_detailed = []
        for row2 in friends:
            friend = self.get_user_by_id(row2)
            friends_detailed.append(
                {
                    "id": friend["id"],
                    "name": friend["name"],
                    "username": friend["username"],
                }
            )
        return friends_detailed

    # Tier 2 - Join
    def get_transactions_by_user(self, user_id):
        """
        Using SQL, returns transactions by user id
        """
        cursor = self.conn.execute(
            "SELECT * FROM transactions INNER JOIN user ON transactions.sender_id=user.id OR transactions.receiver_id=user.id WHERE user.id = ?;",
            (user_id,),
        )
        list = []
        for row in cursor:
            list.append(
                {
                    "sender_id": row[2],
                    "receiver_id": row[3],
                    "amount": row[4],
                    "message": row[5],
                    "accepted": row[6],
                    "timestamp": row[1],
                }
            )
        return list


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
