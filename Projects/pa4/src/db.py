from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table = db.Table(
    "association",
    db.Model.metadata,
    db.Column("course_id", db.Integer, db.ForeignKey("course.id")),
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
)

user_type_table = []


class Course(db.Model):
    """
    Course Model
    """

    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    assignments = db.relationship("Assignment", cascade="delete")
    users = db.relationship(
        "User", secondary=association_table, back_populates="courses"
    )

    def __init__(self, **kwargs):
        """
        Initialize a Task object
        """
        self.code = kwargs.get("code", "")
        self.name = kwargs.get("name", "")

    def serialize(self):
        """
        Serialize a Task object
        """
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "assignments": [a.serialize() for a in self.assignments],
            "instructors": [
                i.simple_serialize()
                for i in self.users
                if i.filter_user_type() == "instructor"
            ],
            "students": [
                s.simple_serialize()
                for s in self.users
                if s.filter_user_type() == "student"
            ],
        }


class Assignment(db.Model):
    """
    Assignment model
    """

    __tablename__ = "assignment"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    due_date = db.Column(db.Integer, nullable=False)
    submissions = db.relationship("Submission", cascade="delete")
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"), nullable=False)

    def __init__(self, **kwargs):
        """
        Initialize a subtask object
        """
        self.title = kwargs.get("title", "")
        self.due_date = kwargs.get("due_date", 0000)
        self.course_id = kwargs.get("course_id")

    def serialize(self):
        return {"id": self.id, "title": self.title, "due_date": self.due_date}


class Submission(db.Model):
    """
    Submission model
    """

    __tablename__ = "submission"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String, nullable=False)
    score = db.Column(db.Integer, nullable=True)
    assignment_id = db.Column(
        db.Integer, db.ForeignKey("assignment.id"), nullable=False
    )

    def __init__(self, **kwargs):
        """
        Initialize a subtask object
        """
        self.user_id = kwargs.get("user_id", 0)
        self.content = kwargs.get("content", "")
        self.score = kwargs.get("score", None)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "score": self.score,
        }


class User(db.Model):
    """
    User Model
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    netid = db.Column(db.String, nullable=False)
    courses = db.relationship(
        "Course", secondary=association_table, back_populates="users"
    )

    def __init__(self, **kwargs):
        """
        Initialize a user object
        """
        self.name = kwargs.get("name", "")
        self.netid = kwargs.get("netid", "")

    def filter_user_type(self):
        """
        Returns the user type
        """
        for x in user_type_table:
            if x.get("user_id") == self.id:
                return x.get("type")

    def serialize(self):
        """
        Serialize a user object
        """
        return {
            "id": self.id,
            "name": self.name,
            "netid": self.netid,
            "courses": [c.serialize() for c in self.courses],
        }

    def simple_serialize(self):
        """
        Serialize a user object without the courses field
        """
        return {"id": self.id, "name": self.name, "netid": self.netid}
