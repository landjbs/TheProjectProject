# structures
from sqlalchemy.sql import *
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base
# forms
from flask_wtf import FlaskForm
from wtforms_alchemy import model_form_factory, ModelForm
from wtforms.validators import (DataRequired, Length, Email, EqualTo,
                                InputRequired, ValidationError, NumberRange)
from wtforms import PasswordField


# define bases
BaseForm = model_form_factory(FlaskForm)
BaseTable = declarative_base()


# define tables
class User(Base, UserMixin):
    ''' Table for Users '''
    __tablename__ = "user"
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



class Project(Base):
    ''' Table for projects '''




# user forms
# class Application(BaseForm):
#     class Meta:
#         model = User
#         exclude = ['role', 'score', 'dot_number']
#         validators = {'name': [DataRequired()],
#                      'company': [DataRequired(), Length(min=1, max=254)],
#                      'email': [DataRequired(), Email(), Length(min=1, max=254)],
#                      'password': [DataRequired(), Length(min=1, max=254)]}
#
#     def validate_email(self, email):
#         if not verify_unique_email(email.data):
#             raise ValidationError('An account is already registered '
#                                   'with that email.')
