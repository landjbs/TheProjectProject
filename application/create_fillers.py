import sys
sys.path.append('.')

from sqlalchemy.sql import exists

from application import db
from application.models import Project, User, Member_Role, Role, Comment, Task, Subject

from application.create_roles import create_roles
from application.create_subjects import create_subjects

create_roles()
create_subjects()
from manager import create_project, add_role_to_user, add_comment


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
             about='I study Math.')]


for user in (users):
    db.session.add(user)
db.session.commit()

ai = Subject.query.get(1)

user1 = db.session.query(User).get(int(1))
user2 = db.session.query(User).get(int(2))


projects = [Project(name='Boogle',
                    oneliner='A raw Python search engine.',
                    summary=('A raw Python search engine hosted on AWS '
                            'using Wikipedia pages as data. Explores NLP '
                            'and ranking techniques. We need database and '
                            'full-stack experts.'),
                    url='boogle.com',
                    application_question='What do you bring to the team?',
                    subjects = [ai],
                    open=True,
                    complete=False,
                    owner=user1,
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
                    subjects = [ai],
                    open=True,
                    complete=False,
                    owner=user1,
                    estimated_time=60,
                    team_size=10,
                    requires_application=True),
            Project(name='Music AI',
                    oneliner='ML for synth design.',
                    summary=('We use ML and VNNs to generate synths that can '
                            'replicate input sounds. I need someone to design '
                            'the synth and someone to help me with the ML.'),
                    url=None,
                    application_question='What is your ML experience?',
                    subjects = [ai],
                    open=True,
                    complete=False,
                    owner=user1,
                    estimated_time=5,
                    team_size=3,
                    requires_application=True),
            Project(name='NonLinGradient Optimizer',
                    oneliner='A new type of batch optimizer.',
                    summary=('We take advantage of batch redundancy to '
                            'run batch gradient through nonlinearity with '
                            'learnable parameters that can help scale learning '
                            'speeds and accelerate convergence of easy params.'),
                    url=None,
                    application_question='Do you like math?',
                    subjects = [ai],
                    open=True,
                    complete=False,
                    owner=user1,
                    estimated_time=3,
                    team_size=2,
                    requires_application=True),
            Project(name='Finance Bots',
                    oneliner='Use RNNs for trading.',
                    summary=('A series of RNN bots trained in tandem to '
                            'evolve real-world strategies in simulated '
                            'environment. With properly-caliberated env, they '
                            'could ship this behavior to the real-world.'),
                    url=None,
                    application_question='',
                    subjects = [ai],
                    open=True,
                    complete=False,
                    owner=user1,
                    estimated_time=3,
                    team_size=2,
                    requires_application=False),
            Project(name='Bio Evolution',
                    oneliner='Modeling yeast evolution.',
                    summary=('Uses numpy to build exp models '
                            'for predicting gene evolution in yeast cultures. '
                            'We can then confirm this in vitrio.'),
                    url=None,
                    application_question='',
                    subjects = [ai],
                    open=True,
                    complete=False,
                    owner=user1,
                    estimated_time=3,
                    team_size=2,
                    requires_application=False),
            Project(name='Fortnite',
                    oneliner='An awesome online game.',
                    summary=('People can build and fight in cartoon style game '
                            'where you drop out of a bus onto an island '
                            'and gather weapons from chests. Need some talented '
                            'AWS people and graphics enthusiasts.'),
                    url=None,
                    application_question='',
                    subjects = [ai],
                    open=True,
                    complete=False,
                    owner=user1,
                    estimated_time=90,
                    team_size=20,
                    requires_application=False),
            Project(name='TheProjectProject',
                    oneliner='A venue for virtual collaboration.',
                    summary=('People apply to join the community by '
                            'submitting past projects. The accepted members '
                            'can post and view project ideas, and easily '
                            'join together to complete them.'),
                    url=None,
                    application_question='',
                    subjects = [ai],
                    open=True,
                    complete=False,
                    owner=user1,
                    estimated_time=90,
                    team_size=20,
                    requires_application=False),
            Project(name='Protein Design',
                    oneliner='AI to design binding proteins.',
                    summary=('Use graph attention networks to generate '
                            'protein sequences that can bind to target '
                            'receptors. We can train in simulated env and add '
                            'complexity over time.'),
                    url=None,
                    application_question='',
                    subjects = [ai],
                    open=True,
                    complete=False,
                    owner=user1,
                    estimated_time=90,
                    team_size=20,
                    requires_application=False)
            ]


def create_fillers():
    for project in projects:
        create_project(project, user1)
    p = db.session.query(Project).get(1)
    t = Task(project=p, author=user2, text='Build front-end.')
    db.session.add(t)
    db.session.commit()
