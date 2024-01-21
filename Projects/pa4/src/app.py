import json

from db import db
from db import user_type_table
from flask import Flask, request
from db import Course
from db import Assignment
from db import User
from db import Submission

app = Flask(__name__)
db_filename = "cms.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


def success_response(data, code=200):
    return json.dumps(data), code


def failure_response(message, code=404):
    return json.dumps({"error": message}), code


@app.route("/")
@app.route("/api/courses/")
def get_courses():
    """
    Endpoint for getting all courses
    """
    courses = [course.serialize() for course in Course.query.all()]
    return success_response({"courses": courses})


@app.route("/api/courses/", methods=["POST"])
def create_course():
    """
    Endpoint for creating a new course
    """
    body = json.loads(request.data)
    new_course = Course(code=body.get("code"), name=body.get("name"))
    db.session.add(new_course)
    db.session.commit()
    return success_response(new_course.serialize(), 201)


@app.route("/api/courses/<int:course_id>/")
def get_course(course_id):
    """
    Endpoint for getting a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    return success_response(course.serialize())


@app.route("/api/courses/<int:course_id>/", methods=["DELETE"])
def delete_course(course_id):
    """
    Endpoint for deleting a course by id
    """
    course = User.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    db.session.delete(course)
    db.session.commit()
    return success_response(course.serialize())


@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Endpoint for creating a new user
    """
    body = json.loads(request.data)
    new_user = User(name=body.get("name"), netid=body.get("netid"))
    db.session.add(new_user)
    db.session.commit()
    return success_response(new_user.serialize(), 201)


@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a user by id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    return success_response(user.serialize())


@app.route("/api/courses/<int:course_id>/add/", methods=["POST"])
def assign_user(course_id):
    """
    Endpoint for assigning a user to a course by id
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    body = json.loads(request.data)
    user_id = body.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    type = body.get("type")

    course.users.append(user)

    user_type_table.append({"user_id": user_id, "course_id": course_id, "type": type})
    print(user_type_table)

    db.session.commit()
    return success_response(course.serialize())


@app.route("/api/courses/<int:course_id>/assignment/", methods=["POST"])
def create_assignment(course_id):
    """
    Create assignment
    """
    course = Course.query.filter_by(id=course_id).first()
    if course is None:
        return failure_response("Course not found!")
    body = json.loads(request.data)
    new_assignment = Assignment(
        title=body.get("title"), due_date=body.get("due_date"), course_id=course_id
    )
    db.session.add(new_assignment)
    db.session.commit()
    return success_response(new_assignment.serialize(), 201)


## Tier 1


@app.route("/api/courses/<int:course_id>/drop/", methods=["POST"])
def drop_student(course_id):
    """
    Drop a student from a course
    """
    body = json.loads(request.data)
    user_id = body.get("user_id")
    user = User.query.filter_by(id=user_id).first()
    course = Course.query.filter_by(id=course_id).first()
    course.users.remove(user)
    db.session.commit()
    return success_response(user.serialize())


@app.route("/api/assignments/<int:assignment_id>/", methods=["POST"])
def update_assignment(assignment_id):
    """
    Endpoint for updating a task by id
    """
    body = json.loads(request.data)
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        return failure_response("Assignment not found!")
    assignment.title = body.get("title", assignment.title)
    assignment.due_date = body.get("due_date", assignment.due_date)
    db.session.commit()
    return success_response(assignment.serialize())


## Tier 2


@app.route("/api/assignments/<int:assignment_id>/submit/", methods=["POST"])
def create_submission(assignment_id):
    """
    Create submission
    """
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        return failure_response("Assignment not found!")
    body = json.loads(request.data)
    new_submission = Submission(
        user_id=body.get("user_id"),
        content=body.get("content"),
        assignment_id=assignment_id,
    )
    db.session.add(new_submission)
    db.session.commit()
    return success_response(new_submission.serialize(), 201)


@app.route("/api/assignments/<int:assignment_id>/grade/", methods=["POST"])
def grade_submission(assignment_id):
    """
    Grade submission
    """
    body = json.loads(request.data)
    submission_id = body.get("submission_id")
    submission = Submission.query.filter_by(id=submission_id).first()
    assignment = Assignment.query.filter_by(id=assignment_id).first()
    if assignment is None:
        return failure_response("Assignment not found!")
    submission.score = body.get("score")
    db.session.commit()
    return success_response(assignment.serialize())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
