db_user = 'admin'
db_password = 'ueIKdWZClnoRZLj6Wu0i'
endpoint = 'collab-commons-rds.c4u7frshhdtj.us-east-1.rds.amazonaws.com:3306'
db_url = 'collab-commons-rds'

# SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{db_user}:{db_password}@{endpoint}/{db_url}'

# VCP ID: vpc-4d83fe37


# Uncomment the line below if you want to work with a local DB
SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'

SQLALCHEMY_POOL_RECYCLE = 3600

WTF_CSRF_ENABLED = True
SECRET_KEY = 'dsaf0897sfdg45sfdgfdsaqzdf98sdf0a'
