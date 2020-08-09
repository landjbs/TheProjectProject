import click
import numpy as np
from faker import Faker
from termcolor import colored
from tqdm import trange, tqdm

from app import db
from app.user.models import User
from app.project.models import Project
from app.subject.models import Subject

from app.subject.create_subjects import create_subjects
from app.badge.create_badges import create_badges


def create_db():
    ''' Creates database '''
    db.create_all()
    return True


def drop_db():
    if click.confirm('Are you sure you want to drop the database?', abort=True):
        db.drop_all()
    return True


def rebuild_db():
    ''' Drops database, creates, and adds statics '''
    print(colored('Dropping...'))
    drop_db()
    create_db()
    add_statics()


def create_badges():
    ''' Drops and creates all badges '''
    create_badges(db)
    return True


def add_statics():
    ''' Adds statics (Subjects, Badges, Admins) to database '''
    create_subjects(db)
    # admins
    db.session.add(
        User(
            name='Landon Smith',
            email='landonsmith@college.harvard.edu',
            password='boop',
            url='https://github.com/landjbs',
            about=('I love AI and NLP. Founder of Strada Routing and '
                   'TheProjectProject!'),
            admin=True
        )
    )
    db.session.commit()


@click.option('--num_users', default=400, help='Number of users.')
@click.option('--num_projects', default=1000, help='Number of projects.')
def populate_db(num_users, num_projects):
    ''' Populates db with seed '''
    fake = Faker()
    # helpers for selection /
    def rand_words(n):
        return ' '.join([fake.word() for _ in range(n)])
    def rand_bool(p_true):
        return np.random.choice([True, False], p=[p_true, (1-p_true)])
    subject_num = Subject.query.count()
    def rand_subjects(n):
        return [Subject.get_by_id(int(id))
                for id in np.random.randint(1, subject_num+1, size=n)]
    # ./helpers
    # fake users
    users = []
    for _ in trange(num_users, desc='Populating Users'):
        name = fake.name()
        user = User(
                name=name,
                email=fake.email(),
                password=(fake.word()+fake.word()),
                url=f'https://github.com/{"_".join(name.split(" ")+[str(i) for i in np.random.randint(0,300,size=10)]).lower()}',
                about=rand_words(10),
                accepted=True
            )
        users.append(user)
    # real users
    for user in tqdm(users, desc='Adding Users'):
        db.session.add(user)
        user.add_subjects(rand_subjects(np.random.randint(0,6)))
    # fake projects
    projects = []
    user_num = User.query.count()
    for _ in trange(num_projects, desc='Populating Projects'):
        requires_application = rand_bool(0.5)
        complete = rand_bool(0.05)
        owner = User.get_by_id(np.random.randint(1, user_num+1))
        subjects = rand_subjects(np.random.randint(0,6))
        projects.append(
            Project(
                owner=owner,
                name=rand_words(2),
                oneliner=rand_words(6),
                summary=rand_words(60),
                url=f'https://{fake.word()}.com',
                complete=complete,
                open=rand_bool(0.8) if not complete else None,
                subjects=subjects,
                requires_application=requires_application if not complete else None,
                application_question=rand_words(6) if requires_application else None,
                estimated_time=max(2, int(np.random.normal(10,4))) if not complete else None,
                team_size=np.random.randint(0,30)
            )
        )
    for project in tqdm(projects, desc='Adding Projects'):
        db.session.add(project)
    db.session.commit()



### list of commands to register ###
command_list = [create_db, drop_db, rebuild_db, create_badges, add_statics,
                populate_db]
