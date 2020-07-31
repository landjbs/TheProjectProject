import os
import boto3
import sys

sys.path.append('.')

from application import db
from application.models import User, Subject

SES_REGION = 'us-east-1'
SES_EMAIL_SOURCE = 'landjbs@gmail.com'
AWS_ACCESS_KEY_ID = None
AWS_SECRET_ACCESS_KEY= None

def send_email(user_email, body):
    ses = boto3.client('ses',
                       region_name=SES_REGION,
                       aws_access_key_id=AWS_ACCESS_KEY_ID,
                       secret_access_key=AWS_SECRET_ACCESS_KEY
                    )
    ses.send_email(Source=SES_EMAIL_SOURCE,
                   Destination={'ToAddresses':[user_email]},
                   Message= {'Subject':{'Data': 'Confirm Your Account'},
                             'Body': {'Text': {'Data': body}}})
    user = User.query.filter_by(email=user_email).first()
    # user.emailed = True
    # db.session.commit()
    print('here')
