'''
Constants defining criteria for each badge
'''


class Badge_Criteria(object):
    def __init__(self):
        self.criteria = {
            ## Verified: have xp>=10000 ##
            'Verified'          :       {10000, 'get_xp'}
        }

    def get_criteria(self, name:str):
        criteria = self.criteria.get(action)
        if not criteria:
            raise ValueError(f'Invalid badge {name}.')
        return criteria


badge_criteria = Badge_Criteria()
