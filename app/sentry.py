'''
Integrates Sentry SDK for error tracking in deployment.
# dependancies
# 'sentry-sdk[flask]==0.16.2'
'''

import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

from app.config import production_config


def register_sentry(dsn):
    '''
    Registers sentry with flask integration using dsn if provided else passes
    '''
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration()],
            release=production_config.VERSION
        )
        return True
    return False
