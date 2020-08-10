from .models import Badge

from tqdm import tqdm


badge_name_list = ['SuperOwner', 'SuperMember', 'Verified']

badge_xp = 1000

def create_badges(db):
    ''' Creates all static badges '''
    badges = [
            ########### SuperOwner: own 50 completed projects ##################
            Badge(name='SuperOwner',
                icon='BadgeIcons/superowner/apple-touch-icon.png',
                description='Own 50 completed projects to showcase your SuperOwner skills!',
                perks=[f'{badge_xp} XP', 'Recommendation Boost in Recommended Project stack',
                       'We will review your projects and connect you with relevant experts',
                       'SuperOwner icon next to your name in all project cards']
                criteria=50,
                evaluator='n_owned_complete'),
            ####################################################################
            ## SuperMember: be a member (not owner) of 50 completed projects ##
            Badge(name='SuperMember',
                icon='BadgeIcons/supermember/apple-touch-icon.png',
                description='Work on 50 completed projects to showcase your SuperMember skills!',
                perks=[f'{badge_xp} XP', 'Recommendation Boost in Recommended Member stack',
                       'SuperMember badge next to your name in all member cards',
                       'We will '],
                criteria=50,
                evaluator='n_member_complete'),
            ####################################################################
            ### WellStudied: have total skill_level>=500 across all subjects ###
            Badge(name='WellStudied',
                icon='BadgeIcons/wellstudied/apple-touch-icon.png',
                description='Have a total skill level of 500 across all subjects to showcase your diverse experience!',
                perks=[f'{badge_xp} XP', 'Recommendation Boost for projects with diverse subjects',
                       'WellStudied badge next to your name in all member cards'],
                criteria=50,
                evaluator='n_member_complete'),
            ####################################################################
            ########## Specialist: have skill_level>=30 on any subject #########
            Badge(name='WellStudied',
                icon='BadgeIcons/wellstudied/apple-touch-icon.png',
                description='Have a total skill level of 500 across all subjects to showcase your diverse experience!',
                perks=[f'{badge_xp} XP', 'Recommendation Boost for projects with diverse subjects',
                       'WellStudied badge next to your name in all member cards'],
                criteria=50,
                evaluator='n_member_complete'),
            ####################################################################
            ## Verified: have xp>=10000 ##
            Badge(name='Verified',
                icon='todo',
                description='The highest honor any social media user can achieve—the coveted Verified badge!',
                perks=['Verified badge next to your name!',
                       'We will review your account and share your story on TheProjectProject social media',
                       'Recommendation Boost in all Recommendation Stacks'],
                criteria=100000,
                evaluator='get_xp')
    ]
    for badge in tqdm(badges):
        db.session.add(badge)
    db.session.commit()
