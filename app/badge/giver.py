''' Gives badges to users for completing tasks '''

from .models import Badge, User_Badge
from .badge_criteria import badge_criteria

def update_superowner(user):
    ''' Allocates superowner user_badge to user as necessary '''
    # get association between user and badge
    user_badge = user.get_badge('SuperOwner')
    # get actual badge from association
    badge = user_badge.get_badge
    # get criteria from badge
    criteria = badge.get_criteria()
    # count number of completed projects
    n_owned_complete = user.n_owned_complete()
    ## allocate ##
    # remove badge if criteria aren't met
    if badge.complete and (n_owned_complete<criteria['projects']):




def update_badges(user):
    ''' Gives badges to user as necessary '''
    ## superowner ##
