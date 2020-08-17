''' configurations for different app runs '''

import os


class base_config(object):
    def __init__(self):
        # SITE
        SITE_NAME = os.environ.get('APP_NAME', 'TheProjectProject')
        # SERVER
        SECRET_KEY = os.environ.get('SECRET_KEY', 'secrets')
        # MAIL
        SES_REGION = os.environ.get('SES_REGION')
        SES_EMAIL_SOURCE = os.environ.get('SES_EMAIL_SOURCE')
        AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
        AWS_SECRET_ACCESS_KEY= os.environ.get('AWS_SECRET_ACCESS_KEY')
        # SQLALCHEMY URI
        DB_USER = os.environ.get('DB_USER', 'admin')
        DB_PASSWORD = os.environ.get('DB_PASSWORD')
        DB_ENDPOINT = os.environ.get('DB_ENDPOINT')
        DB_URL = os.environ.get('DB_URL')
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://%s:%s@%s/%s' % (
            DB_USER,
            DB_PASSWORD,
            DB_ENDPOINT,
            DB_URL
        )
        # SQLALCHEMY SETTINGS
        SQLALCHEMY_POOL_RECYCLE = 3600
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        # REDIS
        QUEUES = ['default']
        # ADMIN
        FLASK_ADMIN_SWITCH = 'orange'
        # FORMS
        WTF_CSRF_ENABLED = True


class dev_config(base_config):
    # SQLALCHEMY URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    # REDIS
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    # STATICS
    SEND_FILE_MAX_AGE_DEFAULT = 0
    # FORMS
    WTF_CSRF_ENABLED = False
    # DEBUGGIN
    ASSETS_DEBUG = True


class production_config(base_config):
    pass
