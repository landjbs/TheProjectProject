from application import db
from application.models import User, Project


# u = User('l', 'e', 'p', 'g', 'a')
# u2 = User('l', 'e', 'p', 'g', 'a')
#
# db.session.add(u)
#
# u = db.session.query(User).get(1)
#
#
# p = Project(name='n',
#             summary='p',
#             url='d',
#             creator=u,
#             open=True,
#             requires_application=True,
#             application_question='b',
#             estimated_time=3.,
#             complete=False)
#
# db.session.add(u)
# db.session.add(u2)
# db.session.commit()

u = db.session.query(User).get(1)
print(u.created_projects)
# print(db.session.query(Project).first().posted_on)
