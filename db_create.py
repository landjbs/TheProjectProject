import os
try:
    os.remove('application/test.db')
except:
    pass

from application import db
from application.models import User
from application.create_roles import create_roles
from application.create_subjects import create_subjects


db.create_all()
create_roles()
create_subjects()

print("DB created.")
