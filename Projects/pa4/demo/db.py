from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

association_table = db.Table(
  "association",
  db.Model.metadata,
  db.Column("task_id", db.Integer, db.ForeignKey("task.id")),
  db.Column("category_id", db.Integer, db.ForeignKey("category.id"))
)

class Task(db.Model):
  """
  Task Model
  """
  __tablename__ = "task"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  description = db.Column(db.String, nullable=False)
  done = db.Column(db.Boolean, nullable=False)
  subtasks = db.relationship("Subtask", cascade="delete")
  categories = db.relationship("Category", secondary=association_table, back_populates="tasks")

  def __init__(self, **kwargs):
    """
    Initialize a Task object
    """
    self.description = kwargs.get("description", "")
    self.done = kwargs.get("done", False)

  def serialize(self):
    """
    Serialize a Task object
    """
    return {
      "id": self.id,
      "description": self.description,
      "done": self.done,
      "subtasks": [s.serialize() for s in self.subtasks],
      "categories": [c.serialize() for c in self.categories]
    }
  
class Subtask(db.Model):
  """
  Subtask model
  """
  __tablename__ = "subtask"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  description = db.Column(db.String, nullable=False)
  done = db.Column(db.Boolean, nullable=False)
  task_id = db.Column(db.Integer, db.ForeignKey("task.id"), nullable=False)

  def __init__ (self, **kwargs):
    """
    Initialize a subtask object
    """
    self.description = kwargs.get("description", '')
    self.done = kwargs.get("done", False)
    self.task_id = kwargs.get("task_id")
  
  def serialize(self):
    return {
    "id": self.id,
    "description": self.description,
    "done": self.done,
    "task_id": self.task_id
  }

class Category(db.Model):
  """
  Category Model
  """
  __tablename__ = "category"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  description = db.Column(db.String, nullable=False)
  color = db.Column(db.String, nullable=False)
  tasks = db.relationship("Task", secondary=association_table, back_populates="categories")

  def __init__(self, **kwargs):
    """
    Initialize a category object
    """
    self.description = kwargs.get("description", "")
    self.color = kwargs.get("color")
  
  def serialize(self):
    """
    Serialize a category object
    """
    return {
      "id": self.id,
      "description": self.description,
      "color": self.color,
      "tasks": [t.serialize() for t in self.tasks]
    }

  def simple_serialize(self):
    """
    Serialize a category object without the tasks field
    """
    return {
      "id": self.id,
      "description": self.description,
      "color": self.color
    }

# implement database model classes
