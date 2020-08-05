''' configurations for different app runs '''


class BaseConfig(object):
    def __init__(self):
        db_user = 'admin'
        db_password = 'jl245o234jDFalsdkjf;kl2j4508usdjilfka'
        endpoint = 'theprojectproject.c4u7frshhdtj.us-east-1.rds.amazonaws.com:3306'
        db_url = 'dev_db'
        SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{db_user}:{db_password}@{endpoint}/{db_url}'

        # VCP ID: vpc-4d83fe37

        # Uncomment the line below if you want to work with a local DB
        # SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

        SEND_FILE_MAX_AGE_DEFAULT = 0
        REDIS_URL = 'redis://redis:6379/0'
        QUEUES = ['default']
        FLASK_ADMIN_SWITCH = 'orange'

        SQLALCHEMY_POOL_RECYCLE = 3600

        WTF_CSRF_ENABLED = True
        # SECRET_KEY = 'cC1YCIWOj9GgWspgNEo2'
        SECRET_KEY = '1v8GEdD0oUBA55MQRkD/D/wS7CGmmSHyatMm0arx'
