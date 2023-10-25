from app import db

class Department(db.Document):
    name = db.StringField(required=True)

class LineManager(db.Document):
    name = db.StringField(required=True)
    email = db.StringField()

class Project(db.Document):
    title = db.StringField(required=True)
    line_manager = db.ReferenceField(LineManager)
    department = db.ReferenceField(Department)
    description = db.StringField()
    has_role_opening = db.BooleanField()
