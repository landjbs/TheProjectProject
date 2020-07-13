from application.models import User, Project


u = User('l', 'e', 'p', 'g', 'a')
u2 = User('l', 'e', 'p', 'g', 'a')
p = Project(name='n',
            summary='p',
            url='d',
            creator=u,
            open=True,
            requires_application=True,
            application_question='',
            estimated_time=3,
            complete=False)
print(u.created_projects)
