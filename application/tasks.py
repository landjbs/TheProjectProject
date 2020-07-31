import time
import sys

sys.path.append('..')

from application import db
from application.models import User, Subject


def send_email(user_email):
    time.sleep(1)
    user = User.query.filter_by(email=user_email).first()
    # user.emailed = True
    # db.session.commit()
    print('here')


send_email('landonsmith@college.harvard.edu')
