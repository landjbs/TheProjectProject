import os
import boto3
import sys

sys.path.append('.')

from application import db
from application.models import User, Subject

SES_REGION = None
AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY= None

def send_email(user_email, body):
    ses = boto3.client('ses',
                       region_name=SES_REGION,
                       aws_access_key_id=AWS_ACCESS_KEY_ID,
                       secret_access_key=AWS_SECRET_ACCESS_KEY
                    )
    ses.send_email(Source=os.getenv('SES_EMAIL_SOURCE'), )
    user = User.query.filter_by(email=user_email).first()
    # user.emailed = True
    # db.session.commit()
    print('here')
