''' Gives badges to users for completing tasks '''

from .models import Badge, User_Badge


def update_superowner(user):
    ''' Allocates superowner user_badge to user as necessary '''
    superowner = Badge.get_by_name('SuperOwner')


def give_badges(user):
    ''' Gives badges to user as necessary '''
    pass
