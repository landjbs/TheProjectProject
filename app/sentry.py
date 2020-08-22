'''
Integrates Sentry SDK for error tracking in deployment.
# dependancies
# 'sentry-sdk[flask]==0.16.2'
'''

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


def register_sentry(dsn):
    ''' Registers sentry with flask integration using dsn from globals '''
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration()]
    )
