import os
try:
    os.remove('application/test.db')
except:
    pass

from application import db
from application.models import User

db.create_all()

print("DB created.")
