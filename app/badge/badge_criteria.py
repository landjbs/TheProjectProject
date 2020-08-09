'''
Constants defining criteria for each badge
'''


class Badge_Criteria(object):
    def __init__(self):
        self.criteria = {
            ## SuperOwner: own 50 completed projects ##
            'SuperOwner'        :       (50, 'n_owned_complete'),
            ## SuperMember: be a member (not owner) of 50 completed projects ##
            'SuperMember'       :       {'projects':50},
            ## WellStudied: have total skill_level>=100 across all subjects ##
            'WellStudied'       :       {'skill':100},
            ## Specialist: have skill_level>=30 on any subject ##
            'Specialist'        :       {'skill':30},
            ## StarStruck: have earned>=200 cumulative stars ##
            'StarStruck'        :       {'stars':200},
            ## WellConnected: work with >=30 different people ##
            'WellConnected'     :       {'users':30},
            ## SetEmUp: create >=100 tasks ##
            'SetEmUp'           :       {'tasks':100},
            ## KnockEmDown: complete >=100 tasks ##
            'KnockEmDown'       :       {'tasks':100},
            ## Verified: have xp>=10000 ##
            'Verified'          :       {10000, 'get_xp'}
        }

    def get_criteria(self, name:str):
        criteria = self.criteria.get(action)
        if not criteria:
            raise ValueError(f'Invalid badge {name}.')
        return criteria


badge_criteria = Badge_Criteria()
