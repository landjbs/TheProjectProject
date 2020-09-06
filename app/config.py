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
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(16))
    # MAIL
    SES_REGION = os.environ.get('SES_REGION', 'us-east-1')
    SES_EMAIL_SOURCE = os.environ.get('SES_EMAIL_SOURCE', 'admin@theprojectproject.io')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY= os.environ.get('AWS_SECRET_ACCESS_KEY')
    REGISTER_MAIL = True
    REQUIRE_EDU = False
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
    FLASK_ADMIN_SWATCH = 'cyborg'
    # FORMS
    WTF_CSRF_ENABLED = True
    ############################ RECOMMENDATION ################################

    ############################## SENTRY ######################################
    SENTRY_DSN = os.environ.get('SENTRY_DSN', default=None)
    ############################# ANALYTICS ####################################
    DOMAIN = 'http://127.0.0.1:5000/'
    # 1 pixel GIF, base64-encoded.
    BEACON = b64decode('R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')
    ANALYTIC_SCRIPT = '''
        (function(){
        var d=document,i=new Image,e=encodeURIComponent;
        i.src='%s/a.gif?url='+e(d.location.href)+'&ref='+e(d.referrer)+'&t='+e(d.title);
        })()'''.replace('\n', '')
    ############################################################################

    def __repr__(self):
        return '<BASE_CONFIG>'


class dev_config(base_config):
    # SERVER_NAME = '127.0.0.1:5000'
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

    def __repr__(self):
        return '<DEV_CONFIG>'


class test_config(base_config):
    # SERVER_NAME = '127.0.0.1:5000'
    TESTING = True

    def __repr__(self):
        return '<TEST_CONFIG>'


class production_config(base_config):
    # site
    # SERVER_NAME = 'https://theprojectproject.io 52.4.87.116'
    DOMAIN = 'https://theprojectproject.io'
    # environment type
    ENV = 'production'
    # enable registration mailing in production only
    REGISTER_MAIL = True
    REQUIRE_EDU = True
    # REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis-theprojectproject.cqci3s.ng.0001.use1.cache.amazonaws.com:6379')
    # ELASTICSEARCH_URL = os.environ.get('ELASTICSEARCH_URL', None)
    PREFERRED_URL_SCHEME = 'https'
    # versioning
    VERSION = 'theprojecproject@0.0.0'

    def __repr__(self):
        return '<PRODUCTION_CONFIG>'
