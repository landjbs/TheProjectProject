import os
import boto3
import sys
from flask import render_template

from app.extensions import rq
from app.user.models import User


SES_REGION = 'us-east-1'
SES_EMAIL_SOURCE = 'admin@theprojectproject.io'
AWS_ACCESS_KEY_ID = 'AKIAQVSLC6YU44B3L5FB'
AWS_SECRET_ACCESS_KEY= '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'

ses = boto3.client('ses',
                   region_name=SES_REGION,
                   aws_access_key_id=AWS_ACCESS_KEY_ID,
                   aws_secret_access_key=AWS_SECRET_ACCESS_KEY
                )

# def send_email(user_email, body):
#     ses.send_email(Source=SES_EMAIL_SOURCE,
#                    Destination={'ToAddresses':[user_email]},
#                    Message= {'Subject':{'Data': 'Confirm Your Account'},
#                              'Body': {'Html': {'Data': body}}})
#     user = User.query.filter_by(email=user_email).first()
#     user.emailed = True
#     db.session.commit()
#     db.session.close()


@rq.job(result_ttl=1)
def send_registration_email(user_id, token):
    print('HERE')
    user = User.query.filter_by(id=user_id).first()
    ses.send_email(
        Source=SES_EMAIL_SOURCE,
        Destination={'ToAddresses': [user.email]},
        Message={
            'Subject': {'Data': 'Confirm Your Account'},
            'Body': {
                'Html': {'Data': render_template('mail/register.mail',
                                                 user=user, token=token)}
            }
        }
    )
    print('COMPLETE')
    return True
