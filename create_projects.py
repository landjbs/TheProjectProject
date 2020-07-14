from application import db
from application.models import Project, User

users = [User(name='Landon Smith',
              email='landonsmith@college.harvard.edu',
              password='boop',
              subjects=None,
              github='www.github.com/landjbs',
              about='I love ML and NLP. CEO of Strada Routing.'),
        User(name='Harrison Oatman',
             email='hroatman@college.harvard.edu',
             password='boop',
             subjects=None,
             github='www.github.com/hroatman',
             about='I study Math.'),]


for user in users:
    db.session.add(user)
db.session.commit()

projects = [Project(name='Boogle',
                    oneliner='A raw Python search engine.',
                    summary=('A raw Python search engine hosted on AWS '
                            'using Wikipedia pages as data. Explores NLP '
                            'and ranking techniques. We need database and '
                            'full-stack experts.'),
                    url='boogle.com',
                    application_question='What do you bring to the team?',
                    open=True,
                    complete=False,
                    creator=db.session.query(User).get(int(1)),
                    estimated_time=10,
                    team_size=4,
                    requires_application=True),
            Project(name='Strada Routing',
                    oneliner='AI trucking logistics.',
                    summary=('Uses Machine Learning to optimize real-world '
                            'vehicle routing problems with respect to '
                            'many trucks, loads and constraints. '),
                    url='stradarouting.com',
                    application_question='What is your ML experience?',
                    open=True,
                    complete=False,
                    creator=db.session.query(User).get(int(1)),
                    estimated_time=10,
                    team_size=4,
                    requires_application=True),
            ]

for project in projects:
    db.session.add(project)
db.session.commit()
