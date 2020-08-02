import os
try:
    os.remove('application/test.db')
except:
    pass

from application import db
from application.models import *

db.drop_all()
db.create_all()

from application.create_fillers import create_fillers

create_fillers()

print("DB created.")

# from manager import add_role_to_user, add_user_to_project
#
# for role in range(1,5):
    # add_role_to_user(db.session.query(Project).get(1), db.session.query(User).get(1),
                     # db.session.query(Role).get(role))
#
# add_user_to_project(db.session.query(Project).get(1), db.session.query(User).get(2),
                    # db.session.query(Role).get(3))

# print(db.session.query(User).get(1).projects.get(1).roles)
