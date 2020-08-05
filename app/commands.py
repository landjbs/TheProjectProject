import click
from faker import Faker

from app import db
from app.models import User


@click.option('--num_users', default=5, help='Number of users.')
def populate_db(num_users):
    ''' Populates db with seed '''
    fake = Faker()
    users = []
    # fake users
    for _ in range(num_users):
        users.append(
            User(
                name=fake.name(),
                email=fake.email(),
                password=(fake.word()+fake.word()),
                github=f'https://github.com/{fake.name()}',
                about=' '.join([fake.word() for _ in range(30)])
            )
        )
        users.append(
            User(
                name='Landon Smith',
                email='landonsmith@college.harvard.edu',
                password='boop',
                github='https://github.com/landjbs',
                about=('I love AI and NLP. Founder of Strada Routing and '
                       'TheProjectProject!'),
                admin=True
            )
        )
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
    drop_db()
    create_db()
