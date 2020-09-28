from flask_assets import Environment
from flask_admin import Admin
from flask_babel import Babel
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_rq2 import RQ
from flask_travis import Travis
from flask_mobility import Mobility
from itsdangerous import URLSafeTimedSerializer
from flask_jsglue import JSGlue
# from werkzeug.contrib.cache import SimpleCache


class FlaskSerializer(URLSafeTimedSerializer):
    ''' Flask-friendly serializer supporting init_app '''
    def __init__(self):
        pass

    def init_app(self, app):
        super(FlaskSerializer, self).__init__(app.secret_key)



assets = Environment()
admin = Admin(template_mode='bootstrap3')
babel = Babel()
csrf = CSRFProtect()
bcrypt = Bcrypt()
# cache = SimpleCache()
limiter = Limiter(key_func=get_remote_address,
                default_limits=['400/minute'])
lm = LoginManager()
migrate = Migrate(compare_type=True)
mobility = Mobility()
rq = RQ()
travis = Travis()
serializer = FlaskSerializer()
jsglue = JSGlue()
