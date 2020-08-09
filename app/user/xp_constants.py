'''
Constants defining xp allocated for each action
'''


class XP_Constants(object):
    def __init__(self):
        self.xps = {
            'star_project'  :   1,
            'earn_star'      :   10,

        }

    def action_xp(self, action:str):
        xp = self.xps.get(action)
        if not xp:
            print(f'WARNING: User action "{action}" is not associated with xp.')
            xp = 0
        return xp


xp_constants = XP_Constants()
