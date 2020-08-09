from .models import Badge

from tqdm import tqdm


def create_badges(db):
    ''' Creates all static badges '''
    badges = [
            # own and complete many projects
            Badge(name='Super-Owner',
                icon='static/BadgeIcons/superowner/apple-touch-icon.png')
            # work on many projects
            # Badge(name='Super-Member',
            #     icon=),
            # have many subject skills
            # Badge('Well-Studied',
            #     icon),
            # # have many points in one subject
            # Badge('Specialist'),
            # # have many stars
            # Badge('Star Struck'),
            # # work with many different users
            # Badge('Well-Connected'),
            # # create many tasks
            # Badge('Set Em Up',),
            # # complete many tasks
            # Badge('Knock Em Down',)
    ]
    for badge in tqdm(badges):
        db.session.add(badge)
    db.session.commit()
