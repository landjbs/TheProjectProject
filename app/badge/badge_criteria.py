'''
Constants defining criteria for each badge
'''


class Badge_Criteria(object):
    def __init__(self):
        self.action_xps = {
            ## SuperOwner: own 50 completed projects ##
            'SuperOwner'        :       {'projects':50},
            ## SuperMember: be a member (and not owner of 50 completed projects) ##
            'SuperMember'       :       {'projects':50},
            ## WellStudied: have skill_level>=5 across 10 subjects ##
            'WellStudied'       :       {'skill':5, 'subjects':10},
            ## Specialist: have skill_level>=30 on any subject ##
            'Specialist'        :       {'skill':30},
            ## StarStruck: have earned>=200 cumulative stars ##
            'StarStruck'        :       {'stars':200},
            ## WellConnected: work with >=30 different people ##
            'WellConnected'     :       {'users':30},
            ## SetEmUp: create >=100 tasks ##
            'SetEmUp'           :       {'tasks':100},
            ## KnockEmDown: complete >=100 tasks ##
            'KnockEmDown'       :       {'tasks':100}
        }

    def get_criteria(self, name:str):
        xp = self.action_xps.get(action)
        if not xp:
            print(f'WARNING: User action "{action}" is not associated with xp.')
            xp = 0
        return xp


badge_criteria = Badge_Criteria()
