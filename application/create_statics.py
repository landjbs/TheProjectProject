import sys
sys.path.append('.')

from application import db
from application.models import Subject, Badge, Admin


subjects = [# data/math/ai:    red
            Subject('AI/ML',                    '#FF0000'),
            Subject('Data Science',             '#FF2A00'),
            Subject('Math',                     '#FF4900'),

            # computational theory:     orange
            Subject('Algorithms',               '#FF7000'),
            Subject('Theory',                   '#FF8F00'),

            # architecture/os:          blue
            Subject('Databases',                '#00B6FF'),
            Subject('Operating Systems',        '#0070FF'),
            Subject('Networks',                 '#0051FF'),
            Subject('Programming Languages',    '#0023FF'),
            Subject('Parallel Computing',       '#0F00FF'),
            Subject('Security/Cryptography',    '#4600FF'),
            Subject('Hacking',                  '#5500FF'),

            # fields:               green
            Subject('Chemistry',                '#7FE300'),
            Subject('Biology',                  '#4CE300'),
            Subject('Engineering',              '#11E300'),
            Subject('Finance',                  '#00E30A'),
            Subject('Gaming',                   '#00E356'),
            Subject('Physics',                  '#00E3A2'),

            # art:                  purple
            Subject('Graphics/Design',          '#AB03FF'),
            Subject('Hardware',                 '#7903FF'),
            Subject('Music',                    '#B303FF'),

            # dev/engineering:      pink
            Subject('Mobile Dev',               '#D503FF'),
            Subject('Web Dev',                  '#E100F0'),
            Subject('Software Engineering',     '#F502C5'),

            # project type          orange
            Subject('Social Issues',            '#F7B914'),
            Subject('Startup',                  '#FFC100'),
            Subject('Research',                 '#FF8000')
            ]


# badges = [Badge('Super-Owner', ),    # own and complete many projects
#           Badge('Super-Member'),     # work on many projects
#           Badge('Well-Studied'),    # have many subject skills
#           Badge('Specialist'),      # have many points in one subject
#           Badge('Star Struck'),      # have many stars
#           Badge('Well-Connected'),  # work with many different users
#           Badge(' ')
#           ]

admins = [Admin(name='Admin', email='landon@theprojectproject.io',
                password='s;kadjflk;asdjf;lkajsdf')]


def create_admins():
    for admin in admins:
        db.session.add(admin)
    db.session.commit()
    return True


def create_subjects():
    for subject in subjects:
        db.session.add(subject)
    db.session.commit()
    return True


def create_badges():
    pass
    # for badge in badges:
    #     db.session.add(badge)
    # db.session.commit()
