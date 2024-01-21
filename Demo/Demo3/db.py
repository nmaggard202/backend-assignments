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
        Secures a connection with the database and stores it into the
        instance variable `conn`
        """
        self.conn = sqlite3.connect("todo.db", check_same_thread=False)
        self.create_task_table()
        self.create_subtask_table()

    # -- TASKS -----------------------------------------------------------

    def create_task_table(self):
        """
        Using SQL, creates a task table
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    done INTEGER NOT NULL
                );
            """
            )
        except Exception as e:
            print(e)

    def delete_task_table(self):
        """
        Using SQL, deletes a task table
        """
        self.conn.execute("DROP TABLE IF EXISTS tasks;")

    def get_all_tasks(self):
        """
        Using SQL, gets all tasks in the task table
        """
        cursor = self.conn.execute("SELECT * FROM tasks;")
        tasks = []

        for row in cursor:
            tasks.append({"id": row[0], "description": row[1], "done": bool(row[2])})
        return tasks

    def insert_task_table(self, description, done):
        """
        Using SQL, adds a new task in the task table
        """
        cursor = self.conn.execute(
            "INSERT INTO tasks (description, done) VALUES (?, ?);", (description, done)
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_task_by_id(self, id):
        """
        Using SQL, gets a task by id
        """
        cursor = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (id,))
        for row in cursor:
            return {"id": row[0], "description": row[1], "done": bool(row[2])}
        return None

    def update_task_by_id(self, id, description, done):
        """
        Using SQL, updates a task by id
        """
        self.conn.execute(
            """
            UPDATE tasks
            SET description = ?, done = ?
            WHERE id = ?;
        """,
            (description, done, id),
        )
        self.conn.commit()

    def delete_task_by_id(self, id):
        """
        Using SQL, deletes a task by id
        """
        self.conn.execute(
            """
            DELETE FROM tasks
            WHERE id = ?;
        """,
            (id,),
        )
        self.conn.commit()

    # -- SUBTASKS --------------------------------------------------------

    def create_subtask_table(self):
        """
        Using SQL, creates a subtask table.
        """
        try:
            self.conn.execute(
                """
                CREATE TABLE IF NOT EXISTS subtasks(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    done INTEGER NOT NULL,
                    task_id INTEGER NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                );
                """
            )
        except Exception as e:
            print(e)

    def delete_subtask_table(self):
        self.conn.execute("DROP TABLE IF EXISTS subtasks")

    def get_all_subtasks(self):
        """
        Using SQL, get all subtasks.
        """
        cursor = self.conn.execute("SELECT * FROM subtasks")
        subtasks = []
        for row in cursor:
            subtasks.append(
                {
                    "id": row[0],
                    "description": row[1],
                    "done": bool(row[2]),
                    "task_id": row[3],
                }
            )
        return subtasks

    def insert_subtask(self, description, done, parent_id):
        """
        Using SQL, add a new subtask into the subtask table
        """
        cursor = self.conn.execute(
            "INSERT INTO subtasks (description, done, task_id) VALUES (?, ?, ?);",
            (description, done, parent_id),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_subtask_by_id(self, id):
        """
        Using SQL, get a subtask by its id
        """
        cursor = self.conn.execute("SELECT * FROM subtasks where ID = ?", (id,))
        for row in cursor:
            return {
                "id": row[0],
                "description": row[1],
                "done": bool(row[2]),
                "task_id": row[3],
            }
        return None

    def get_subtasks_of_task(self, parent_id):
        """
        Using SQL, get all the subtasks given a task id.
        """
        cursor = self.conn.execute(
            "SELECT * FROM subtasks WHERE task_id = ?", (parent_id,)
        )
        subtasks = []

        for row in cursor:
            subtasks.append(
                {
                    "id": row[0],
                    "description": row[1],
                    "done": bool(row[2]),
                    "task_id": row[3],
                }
            )
        return subtasks


# Only <=1 instance of the database driver
# exists within the app at all times
DatabaseDriver = singleton(DatabaseDriver)
