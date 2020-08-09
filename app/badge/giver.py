''' Gives badges to users for completing tasks '''

from .models import Badge, User_Badge


def update_superowner(user):
    ''' Allocates superowner user_badge to user as necessary '''
    superowner = Badge.get_by_name('SuperOwner')
    if not superowner:



def update_badges(user):
    ''' Gives badges to user as necessary '''
    ## superowner ##
    badge = user.get_badge('SuperOwner')
    n_owned_complete = user.n_owned_complete()
    if n_owned_complete>0:
        
