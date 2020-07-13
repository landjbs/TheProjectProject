from application import db
from application.models import User, Project, Subject


# ai = Subject(name='ai')
#
# u = User(name='landon',
#         email='land@',
#         password='boop',
#         subjects=[ai],
#         github='github',
#         about='Hi')
#
# db.session.add(ai)
# db.session.add(u)

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


# db.session.commit()

print(db.session.query(User).first().subjects)
