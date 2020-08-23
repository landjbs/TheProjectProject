import unittest

from app import create_app
from app.config import test_config
from app.database import db
from app.user.models import User
from sqlalchemy.sql.expression import func
from app.fake import fake, rand_words, rand_bool, rand_subjects, rand_badges


admin_email = 'landonsmith@college.harvard.edu'
admin_password = 'boop'


class TestCase(unittest.TestCase):
    def setUp(self):
        app = create_app(test_config, register_admin=False)
        db.app = app  # hack for using db.init_app(app) in app/__init__.py
        self.app = app.test_client()

    def tearDown(self):
        pass

    def login(self, username, password):
        return self.app.post('/login', data=dict(
            email=admin_email,
            password=admin_password
        ), follow_redirects=True)

    def apply(self):
        password = rand_words(1)
        return self.app.post('/apply', data=dict(
            name=fake.name(),
            email=fake.email(),
            url=None,
            about=rand_words(10)[:500],
            password=password,
            confirm=password,
            subjects=None
        ), follow_redirects=True)

    # def edit_user(self, user, email):
    #     return self.app.post('/user/edit/%s' % user.id, data=dict(
    #         username=user.username,
    #         email=user.email,
    #     ), follow_redirects=True)

    def delete_user(self, uid):
        return self.app.get('/user/delete/%s' % uid, follow_redirects=True)

    ## error handling ##
    def test_404(self):
        resp = self.app.get('/nope', follow_redirects=True)
        assert resp.data, '404'

    ## base pages ##
    def test_index(self):
        resp = self.app.get('/index', follow_redirects=True)
        assert resp.data, 'Index'

    def test_about(self):
        resp = self.app.get('/about', follow_redirects=True)
        assert resp.data, 'About'

    def test_contact(self):
        resp = self.app.get('/contact', follow_redirects=True)
        assert resp.data, 'Contact'

    def test_login(self):
        resp = self.login(admin_email, admin_password)
        assert resp.data, 'Login'

    def test_logout(self):
        resp = self.login(admin_email, admin_password)
        resp = self.app.get('/logout', follow_redirects=True)
        assert resp.data, 'Logout'

    def test_apply(self):
        # TODO: make this actually validate and work
        resp = self.apply()
        # assert (resp._status_code != 400), 'Bad Request'
        assert resp.data, 'Sent verification email to %s' % email

    # def test_edit_user(self):
    #     user = User.query.order_by(func.random()).first()
    #     resp = self.login(admin_email, admin_password)
    #     resp = self.edit_user(user, email=fake.email())
    #     assert resp.data, 'User %s edited' % user.username

    # def test_delete_user(self):
    #     user = User.query.order_by(func.random()).first()
    #     resp = self.login(admin_email, admin_password)
    #     resp = self.delete_user(user.id)
    #     assert resp.data, 'User %s deleted' % user.username

    # def test_user_list(self):
    #     resp = self.login(admin_email, admin_password)
    #     resp = self.app.get('/user/list', follow_redirects=True)
    #     assert resp.data, 'Users'


if __name__ == '__main__':
    unittest.main()
