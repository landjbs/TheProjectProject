from .models import Badge

from tqdm import tqdm


def create_badges(db):
    ''' Creates all static badges '''
    badges = [
            ########### SuperOwner: own 50 completed projects ##################
            Badge(name='SuperOwner',
                icon='static/BadgeIcons/superowner/apple-touch-icon.png',
                criteria=50,
                evaluator='n_owned_complete'),
            ####################################################################
            ## SuperMember: be a member (not owner) of 50 completed projects ##
            Badge(name='SuperMember',
                icon='static/BadgeIcons/supermember/apple-touch-icon.png',
                criteria=50,
                evaluator='n_owned_complete')
            ####################################################################
            ## Verified: have xp>=10000 ##
            Badge(name='Verified',
                icon='todo',
                criteria=100000,
                evaluator='get_xp')
    ]
    for badge in tqdm(badges):
        db.session.add(badge)
    db.session.commit()
