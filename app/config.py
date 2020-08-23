''' configurations for different app runs '''

import os
from base64 import b64decode

# from dotenv import load_dotenv

# # load .env config file
# basedir = os.path.abspath(os.path.dirname('..'))
# load_dotenv(os.path.join(basedir, '.env'))


class base_config(object):
    # SITE
    SITE_NAME = os.environ.get('APP_NAME', 'TheProjectProject')
    # SERVER
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # MAIL
    SES_REGION = os.environ.get('SES_REGION', 'us-east-1')
    SES_EMAIL_SOURCE = os.environ.get('SES_EMAIL_SOURCE', 'admin@theprojectproject.io')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY= os.environ.get('AWS_SECRET_ACCESS_KEY')
    REGISTER_MAIL = False
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
    FLASK_ADMIN_SWATCH = 'cerulean'
    # FORMS
    WTF_CSRF_ENABLED = True
    # SENTRY (will not enable error notification if no DSN exported)
    SENTRY_DSN = os.environ.get('SENTRY_DSN', default=None)
    #################### ANALYTICS #################
    # 1 pixel GIF, base64-encoded.
    DOMAIN = 'http://127.0.0.1:5000'  # TODO: change me.
    BEACON = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')
    ANALYTIC_SCRIPT = '''
        (function(){
        var d=document,i=new Image,e=encodeURIComponent;
        i.src='%s/a.gif?url='+e(d.location.href)+'&ref='+e(d.referrer)+'&t='+e(d.title);
        })()'''.replace('\n', '')


class dev_config(base_config):
    # SQLALCHEMY URI
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    # REDIS
    # REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
    ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', None) #'http://localhost:9200'
    # STATICS
    SEND_FILE_MAX_AGE_DEFAULT = 0
    # FORMS
    WTF_CSRF_ENABLED = True
    # DEBUGGING
    ASSETS_DEBUG = True
    ENV = 'development'


class test_config(base_config):
    TESTING = True


class production_config(base_config):
    # environment type
    ENV = 'production'
    # whether to enable registration mailing
    REGISTER_MAIL = True
    # REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis-theprojectproject.cqci3s.ng.0001.use1.cache.amazonaws.com:6379')
    # ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', None)
    PREFERRED_URL_SCHEME = 'https'
