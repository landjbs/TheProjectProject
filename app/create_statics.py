import sys
sys.path.append('.')

from application import db
from application.models import Subject, Badge


# badges = [Badge('Super-Owner', ),    # own and complete many projects
#           Badge('Super-Member'),     # work on many projects
#           Badge('Well-Studied'),    # have many subject skills
#           Badge('Specialist'),      # have many points in one subject
#           Badge('Star Struck'),      # have many stars
#           Badge('Well-Connected'),  # work with many different users
#           Badge(' ')
#           ]

# admins = [Admin_User(name='Admin', email='landon@theprojectproject.io',
#                      password='boop')]
#
#
def create_admins():
    pass
    # for admin in admins:
    #     db.session.add(admin)
    # db.session.commit()
    # return True


def create_subjects():
    for subject in subjects:
        db.session.add(subject)
    db.session.commit()
    db.session.close()
    return True


def create_badges():
    pass
    # for badge in badges:
    #     db.session.add(badge)
    # db.session.commit()
