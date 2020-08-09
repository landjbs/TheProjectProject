''' Gives badges to users for completing tasks '''

from .models import Badge, User_Badge
from .badge_criteria import badge_criteria

def update_superowner(user):
    ''' Allocates superowner user_badge to user as necessary '''
    badge = user.get_badge('SuperOwner')
    n_owned_complete = user.n_owned_complete()
    if badge.complete and (n_owned_complete):




def update_badges(user):
    ''' Gives badges to user as necessary '''
    ## superowner ##
