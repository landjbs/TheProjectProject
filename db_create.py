import os
try:
    os.remove('application/test.db')
except:
    pass

from application import db
from application.models import *
from termcolor import colored

if input('Database already exists. Are you sure you want to delete? (y/n): ')=='y':
    print(colored('Dropping tables...', color='yellow'), end='\r')
    db.drop_all()
    print(colored('COMPLETE: Dropping tables', color='green'))
    print(colored('Building tables...', color='yellow'), end='\r')
    db.create_all()
    print(colored('COMPLETE: Buidling tables', color='green'))
    print(colored('Creating objects...', color='yellow'), end='\r')
    from application.create_fillers import create_fillers
    create_fillers()
    print(colored('COMPLETE: Creating objects', color='green'))
    print("DB created.")
    db.session.close()
else:
    print('Database rebuild prevented.')

# from manager import add_role_to_user, add_user_to_project
#
# for role in range(1,5):
    # add_role_to_user(db.session.query(Project).get(1), db.session.query(User).get(1),
                     # db.session.query(Role).get(role))
#
# add_user_to_project(db.session.query(Project).get(1), db.session.query(User).get(2),
                    # db.session.query(Role).get(3))

# print(db.session.query(User).get(1).projects.get(1).roles)
