from application import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
    # id primary key
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(128), index=True, unique=False,
                     info={'label':'Name'})
    # email
    email = db.Column(db.String(254), unique=False, nullable=False,
                      info={'label':'Havard Email '})
    # password
    password = db.Column(db.String(254), nullable=False,
                         info={'label':'Password'})
    # github # TODO: figure out how to validate github
    github = db.Column(db.String(254), nullable=False,
                         info={'label':'Github'})
    # about
    about = db.Column(db.String(500), nullable=False,
                      info={'label':'About'})
    # status {0:applied, 1:member, 2:admin}
    accepted = db.Column(db.Boolean, nullable=False)

    def __init__(self, name, email, password, github, about):
        self.name = name
        self.email = email
        self.password = self.set_password(password)
        self.github = github
        self.about = about
        self.accepted = False # status set to "applied"

    def __repr__(self):
        return '<User %r>' % self.name

    def set_password(self, password):
        return generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        return True

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
