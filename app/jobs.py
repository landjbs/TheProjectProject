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


@rq.job
def send_registration_email(user, url):
    ses.send_email(
        Source=SES_EMAIL_SOURCE,
        Destination={'ToAddresses': [user.email]},
        Message={
            'Subject': {'Data': 'Confirm Your Application'},
            'Body': {
                'Html': {'Data': render_template('mail/register.mail',
                                                 user=user, url=url)}
            }
        }
    )
    return True


@rq.job
def send_confirmation_email(user):
    ses.send_email(
        Source=SES_EMAIL_SOURCE,
        Destination={'ToAddresses': [user.email]},
        Message={
            'Subject': {'Data': 'Thanks For Applying!'},
            'Body': {
                'Html': {'Data': render_template('mail/confirm.mail',
                                                 user=user)}
            }
        }
    )
    return True


@rq.job
def send_acceptance_email(user):
    urls = {'login':  url_for('admin.login')}
    ses.send_email(
        Source=SES_EMAIL_SOURCE,
        Destination={'ToAddresses': [user.email]},
        Message={
            'Subject': {'Data': 'Congratulations!'},
            'Body': {
                'Html': {'Data': render_template('mail/accept.mail',
                                                 user=user, urls=urls)}
            }
        }
    )
    return True
