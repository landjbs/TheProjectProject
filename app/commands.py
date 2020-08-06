import click
from faker import Faker
from termcolor import colored

from app import db
from app.user.models import User


@click.option('--num_users', default=5, help='Number of users.')
def populate_db(num_users):
    ''' Populates db with seed '''
    fake = Faker()
    users = []
    # fake users
    for _ in range(num_users):
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
