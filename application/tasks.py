import time

sys.path.append('.')

from application import db
from application.models import User, Subject


def send_email(user_email):
    time.sleep(1)
    user = User.query.filter_by(email=user_email).first()
    print('here')    
