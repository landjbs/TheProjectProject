''' configurations for different app runs '''

import os


class base_config(object):
    def __init__(self):
        # SITE
        SITE_NAME = os.environ.get('APP_NAME', 'TheProjectProject')
        # SERVER
        SECRET_KEY = os.environ.get('SECRET_KEY', 'secrets')
        # MAIL
        SES_REGION = 'us-east-1'
        SES_EMAIL_SOURCE = 'admin@theprojectproject.io'
        AWS_ACCESS_KEY_ID = 'AKIAQVSLC6YU44B3L5FB'
        AWS_SECRET_ACCESS_KEY= '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'
        # SQLALCHEMY URI
        # uri = f'mysql+pymysql://admin:sk90jal;skdjn,235#adsfjalasdf#%n2sdf@theprojectproject.c4u7frshhdtj.us-east-1.rds.amazonaws.com:3306/theprojectproject_production'
        # db_user = 'admin'
        # db_password = 'jl245o234jDFalsdkjf;kl2j4508usdjilfka'
        # endpoint = 'theprojectproject.c4u7frshhdtj.us-east-1.rds.amazonaws.com:3306'
        # db_url = 'dev_db'
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
        self.FLASK_ADMIN_SWITCH = 'orange'
        # FORMS
        self.WTF_CSRF_ENABLED = True
        
        self.SECRET_KEY = '1v8GEdD0oUBA55MQRkD/D/wS7CGmmSHyatMm0arx'


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
