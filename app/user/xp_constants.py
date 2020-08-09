'''
Constants defining xp allocated for each action
'''


class XP_Constants(object):
    def __init__(self):
        self.constants = {

        }

    def action_xp(self, action:str):
        xp = self.constants.get(action)
        if not xp:
            xp = 0
        return xp
