import click
import numpy as np
from faker import Faker
from termcolor import colored
from tqdm import trange

from app import db
from app.user.models import User
from app.project.models import Project


# helpers for selection



@click.option('--num_users', default=5, help='Number of users.')
@click.option('--num_projects', default=5, help='Number of projects.')
def populate_db(num_users):
    ''' Populates db with seed '''
    fake = Faker()
    users = []
    # fake users
    for _ in trange(num_users, desc='Populating Users'):
        name = fake.name()
        users.append(
            User(
                name=name,
                email=fake.email(),
                password=(fake.word()+fake.word()),
                url=f'https://github.com/{"_".join(name.split(" ")).lower()}',
                about=' '.join([fake.word() for _ in range(30)])
            )
        )
    # real users
    users.append(
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
    # fake projects
    projects = []
    for _ in trange(num_projects):
        projects.append(
            Project(
                name=f'{fake.word()} {fake.word()}',
                oneliner=' '.join([fake.word() for _ in range(6)]),
                summary=' '.join([fake.word() for _ in range(60)]),
                url=f'https://{fake.word()}.com',
                open=np.random.choice([True, False], p=[0.8,0.2]),
                subjects=None, # TODO:
                requires_application=
            )
        )
    # add all objects
    for user in users:
        db.session.add(user)
    db.session.commit()


def create_db():
    ''' Creates database '''
    db.create_all()
    return True


def drop_db():
    if click.confirm('Are you sure you want to drop the database?', abort=True):
        db.drop_all()
    return True


def rebuild_db():
    ''' Drops database and then creates '''
    print(colored('Dropping...'))
    drop_db()
    create_db()
