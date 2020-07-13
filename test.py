from application import db
from application.models import User, Project


u = User('l', 'e', 'p', 'g', 'a')
# u2 = User('l', 'e', 'p', 'g', 'a')

db.session.add(u)

p = Project(name='n',
            summary='p',
            url='d',
            creator=u,
            open=True,
            requires_application=True,
            application_question='',
            estimated_time=3,
            complete=False)

db.session.add(p)
db.session.commit()

# print(db.session.query(Project).first())
