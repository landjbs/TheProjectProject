from .models import Badge


def create_badges(db):
    ''' Creates all static badges '''
    badges = [
            # own and complete many projects
            Badge('Super-Owner', ),
            # work on many projects
            Badge('Super-Member'),
            # have many subject skills
            Badge('Well-Studied'),
            # have many points in one subject
            Badge('Specialist'),
            # have many stars
            Badge('Star Struck'),
            # work with many different users
            Badge('Well-Connected'),
            # create many tasks
            Badge('Set Em Up',),
            # complete many tasks
            Badge('Knock Em Down',)
    ]
