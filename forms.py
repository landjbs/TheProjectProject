# structs
from sqlalchemy.sql import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Column, Integer, String, DateTime,
                        Sequence, Float,PrimaryKeyConstraint, Binary,
                        ForeignKey)
from sqlalchemy_utils import DateTimeRangeType, PasswordType
# security
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
# forms
from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory, ModelForm
from wtforms.validators import (DataRequired, Length, Email, EqualTo,
                                InputRequired, ValidationError, NumberRange)
from wtforms import PasswordField


# define bases
BaseTable = declarative_base()
BaseForm = model_form_factory(FlaskForm)


# define tables
class User(BaseTable, UserMixin):
    ''' Table for Users '''
    __tablename__ = 'user'
    # primary key id
    id = Column(Integer, Sequence('poi_id_seq'), primary_key=True)
    # name
    name = Column(String(254), unique=False, nullable=False,
                  info={'label':'Name'})
    # email
    email = Column(String(254), unique=False, nullable=False,
                   info={'label':'Email Address'})
    # password
    password = Column(String(254), nullable=False, info={'label':'Password'})
    # interests
    # projects = relationship('Project', backref='user', lazy=True,
                            # cascade="all, delete-orphan")

    def __repr__(self):
        return '<User %r>' % self.name

    def set_password(self, password):
        self.password = generate_password_hash(password)

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


# class Project(Base):
#     ''' Table for projects '''
#     # primary key id
#     id = Column(Integer, Sequence('poi_id_seq'), primary_key=True)
#     # name
#     name = Column(String(254), unique=False, nullable=False,
#                 info={'label':'Name'})
#     #
#     about = Column(String(1000), unique=False, nullable=False,
#                    info={'label':'about'})
#     members =


# user forms
class Application(BaseForm):
    class Meta:
        model = User
        # exclude = ['role', 'score', 'dot_number']
        validators = {'name': [DataRequired()],
                     'email': [DataRequired(), Email(), Length(min=1, max=254)],
                     'password': [DataRequired(), Length(min=1, max=254)]}

    def validate_email(self, email):
        if not verify_unique_email(email.data):
            raise ValidationError('An account is already registered '
                                  'with that email.')
