from flask_assets import Environment
from flask_admin import Admin
# from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
# from flask_mail import Mail
from flask_migrate import Migrate
from flask_rq2 import RQ
from flask_travis import Travis
# from werkzeug.contrib.cache import SimpleCache


assets = Environment()
admin = Admin(template_mode='bootstrap3')
# babel = Babel()
csrf = CSRFProtect()
########## BCRYPT ##############
bcrypt = Bcrypt()
################################
# cache = SimpleCache()
########## LIMITER ##############
limiter = Limiter(key_func=get_remote_address)
################################

######### LOGIN MANAGER #########
lm = LoginManager()
################################

########### MIGRATION ##########
migrate = Migrate()
################################
# mail = Mail()
rq = RQ()
travis = Travis()
