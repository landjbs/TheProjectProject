import click
import numpy as np
from faker import Faker
from termcolor import colored
from tqdm import trange, tqdm

from app import db
from app.user.models import User
from app.company.models import Company
from app.project.models import Project
from app.subject.models import Subject
from app.badge.models import Badge, User_Badge
from app.competition.models import Competition

from app.subject.create_subjects import create_subjects
from app.badge.create_badges import create_badges
from app.fake import fake, rand_words, rand_bool, rand_subjects, rand_badges


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
    drop_db()
    create_db()
    add_statics()


def add_badges():
    ''' Drops and creates all badges '''
    create_badges(db)
    return True


def add_statics():
    ''' Adds statics (Subjects, Badges, Admins) to database '''
    create_subjects(db)
    add_badges()
    # admins
    db.session.add(
        User(
            name='Landon Smith',
            email='landonsmith@college.harvard.edu',
            password='boop',
            about=('I love AI and NLP. Founder of Strada Routing and '
                   'TheProjectProject!'),
            admin=True
        )
    )
    db.session.commit()


@click.option('--num_users', default=3, help='Number of users.')
@click.option('--num_projects', default=5, help='Number of projects.')
def populate_db(num_users, num_projects):
    ''' Populates db with seed '''
    fake = Faker()
    # fake users
    users = []
    for _ in trange(num_users, desc='Populating Users'):
        try:
            name = fake.name()
            user = User(
                    name=name,
                    email=fake.email(),
                    password='boop',
                    about=rand_words(10),
                    accepted=True
                )
            users.append(user)
        except Exception as e:
            print(f'Could not add: {e}')
    # real users
    for user in tqdm(users, desc='Adding Users'):
        try:
            db.session.add(user)
            user.add_subjects(rand_subjects(np.random.randint(10,30)))
            badges = rand_badges(np.random.randint(0,4))
            for badge in badges:
                user.badges.append(User_Badge(badge=badge, earned=True))
        except Exception as e:
            print(f'Could not add: {e}')
    # fake projects
    projects = []
    user_num = User.query.count()
    for _ in trange(num_projects, desc='Populating Projects'):
        requires_application = rand_bool(0.5)
        complete = rand_bool(1)
        owner = User.get_by_id(np.random.randint(1, user_num+1))
        subjects = rand_subjects(np.random.randint(0,6))
        projects.append(
            Project(
                owner=owner,
                name=rand_words(2),
                oneliner=rand_words(6),
                summary=rand_words(60),
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
    # # NOTE: finish populating competitions
    # fake competitions
    # competitions = []
    # for _ in trange(num_competitions, desc='Populating Competitions'):
    #     competitions.append(
    #         Competition(
    #             name=rand_words(2),
    #             sponsor=rand_words(2),
    #             description=rand_words(40),
    #             prize=rand_words(5),
    #         )
    #     )
    db.session.commit()


def add_test():
    # admins
    user = User.create(
            name='Test User',
            email='test@college.harvard.edu',
            password='boop',
            about=('I am a test user for TheProjectProject. Excited to be here.'),
            accepted=True

    )
    user.add_subjects(set(Subject.get_by_id(int(id)) for id in np.random.randint(1, 10+1, size=4)))
    return True


# def reindex():
#     ''' Reindexes searchables '''
#     for searchable in tqdm([User, Project, Subject], desc='Reindexing'):
#         searchable.reindex()
#     return True

@click.argument('text')
@click.argument('name', default=None)
@click.argument('redirect', default=None)
@click.option('--important', default=True, type=bool)
def notify_all(text, name, redirect, important):
    User.notify_all(
        text=str(text),
        name=str(name),
        redirect=str(redirect),
        important=bool(important)
    )
    return True

### list of commands to register ###
command_list = [create_db, drop_db, rebuild_db, add_badges, add_statics,
                populate_db, add_test, notify_all]


### elasticsearch stuff ##
# To have launchd start elasticsearch now and restart at login:
#   brew services start elasticsearch
# Or, if you don't want/need a background service you can just run:
#   elasticsearch
