import sys
sys.path.append('.')

from application import db
from application.models import Subject, Badge


subjects = [Subject('AI/ML',                    '#FF5733'),
            Subject('Algorithms',               '#FFA533'),
            Subject('Databases',                '#FFF033'),
            Subject('Chemistry',                '#FFF033'),
            Subject('Biology',                  '#B8FF33'),
            Subject('Data Science',             '#FFF033'),
            Subject('Finance',                  '#00B6FF'),
            Subject('Graphics/Design',          '#58FF33'),
            Subject('Gaming',                   '#FF00B9'),
            Subject('Hacking',                  '#33FFCA'),
            Subject('Hardware',                 '#FF3333'),
            Subject('Math',                     '#3342FF'),
            Subject('Music',                    '#3342FF'),
            Subject('Mobile Dev',               '#E333FF'),
            Subject('Networking',               '#33FFFF'),
            Subject('Operating Systems',        '#33FFFF'),
            Subject('Parallel Computing',       '#335BFF'),
            Subject('Web Dev',                  '#8D33FF'),
            Subject('Programming Languages',    '#FF33E9'),
            Subject('Physics',                  '#B8FF33'),
            Subject('Research',                 '#DDFF33'),
            Subject('Security/Cryptography',    '#49FF33'),
            Subject('Software Engineering',     '#AF33FF'),
            Subject('Social Issues',            '#33DAFF'),
            Subject('Startup',                  '#33C1FF'),
            Subject('Theory',                   '#3352FF')]


# badges = [Badge('Super-Owner', ),    # own and complete many projects
#           Badge('Super-Member'),     # work on many projects
#           Badge('Well-Studied'),    # have many subject skills
#           Badge('Specialist'),      # have many points in one subject
#           Badge('Star Struck'),      # have many stars
#           Badge('Well-Connected'),  # work with many different users
#           Badge(' ')
#           ]


def create_subjects():
    for subject in subjects:
        db.session.add(subject)
    db.session.commit()


def create_badges():
    pass
    # for badge in badges:
    #     db.session.add(badge)
    # db.session.commit()
