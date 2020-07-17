from manager import add_user_to_project, create_project, create_role, db
from application.models import Project, User, Role

user = User('Landon', 'b', '', '', '', '')
user2 = User('2', 'l', '', '', '', '')
project = Project('b', '', '', '', '', False, '', 19, 10, False, user)
role = db.session.query(Role).filter_by(name='Data Scientist').first()


create_project(project, user)

for x in db.session.query(Project):
    for m in x.members:
        print(m.user, m.role)


add_user_to_project(project, user2, role)

for x in db.session.query(Project):
    for m in x.members:
        print(m.user, m.role)

# from application import db
# from application.models import User, Project, Subject


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
