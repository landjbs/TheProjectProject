'''
Constants defining xp allocated for each action
'''


class XP_Constants(object):
    def __init__(self):
        self.verified_xp = 100000
        self.action_xps = {
            ## stars ##
            'star_project'      :   1,
            'earn_star'         :   50,
            ## collab ##
            'send_collab'       :   5,
            'recieve_collab'    :   10,
            ## tasks ##
            'add_task'          :   30,
            'complete_task'     :   50,
            ## projects ##
            'complete_project'  :   500,
            'join_project'      :   100,
            ## badges ##
            'earn_badge'        :   5000
        }

    def action_xp(self, action:str):
        xp = self.action_xps.get(action)
        if not xp:
            print(f'WARNING: User action "{action}" is not associated with xp.')
            xp = 0
        return xp


xp_constants = XP_Constants()
