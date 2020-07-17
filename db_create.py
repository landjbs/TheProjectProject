import os
try:
    os.remove('application/test.db')
except:
    pass

from application import db
from application.models import User

db.create_all()

from application.create_fillers import create_fillers

create_fillers()


print("DB created.")
