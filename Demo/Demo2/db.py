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
        self.conn = sqlite3.connect("todo.db", check_same_thread=False)
        self.create_task_table()
    
    def create_task_table(self):
        """
        Using SQL, creates a task table.
        """
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS task(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            done BOOLEAN NOT NULL
            );"""
        )
    
    def delete_task_table(self):
        """
        Using SQL, deletes a task table
        """
        self.conn.execute("""DROP TABLE IF EXISTS task""")
    
    def get_all_tasks(self):
        """
        Using SQL, returns all tasks in a table
        """
        cursor = self.conn.execute("SELECT * FROM task")
        tasks = []
        for row in cursor:
            tasks.append({"id":row[0], "description":row[1], "done":row[2]})
        return tasks

    def get_task_by_id(self, id):
        """
        Using SQL, returns a task by id
        """
        cursor = self.conn.execute("SELECT * FROM task WHERE id = ?;",(id, ))
        for row in cursor:
            return ({"id":row[0], "description":row[1], "done":row[2]})
        return None

    def insert_task_table(self, description, done):
        """
        Using SQL, inserts a task into the task table
        """
        cursor = self.conn.execute("INSERT INTO task(description, done) VALUES (?, ?);",(description, done))
        self.conn.commit()
        return cursor.lastrowid
    
    def update_task_by_id(self, description, done, id):
        """
        Using SQL, updates a task in the table
        """
        self.conn.execute("""UPDATE task
                          SET description = ?,
                          done = ?
                          WHERE id = ?;
                        """, (description, done, id))
        self.conn.commit()
    
    def delete_task_by_id(self, id):
        """
        Using SQL, deletes a task from a table
        """
        self.conn.execute("DELETE FROM task WHERE id = ?;", (id, ))
        self.conn.commit()



# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
