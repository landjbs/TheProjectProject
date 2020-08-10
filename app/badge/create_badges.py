from .models import Badge

from tqdm import tqdm


badge_name_list = ['SuperOwner', 'SuperMember', 'WellStudied', 'Specialist',
                   'StarStruck', 'WellConnected', 'SetEmUp', 'KnockEmDown',
                    'Verified']
badge_xp = 1000

def create_badges(db):
    ''' Creates all static badges '''
    badges = [
            ########### SuperOwner: own 50 completed projects ##################
            Badge(name='SuperOwner',
                description='Own 50 completed projects to showcase your SuperOwner skills!',
                perks=[f'{badge_xp} XP', 'Recommendation Boost in Recommended Project stack',
                       'We will review your projects and connect you with funding/compute if possible',
                       'SuperOwner icon next to your name in all project cards'],
                criteria=50,
                evaluator='n_owned_complete'),
            ####################################################################
            ## SuperMember: be a member (not owner) of 50 completed projects ##
            Badge(name='SuperMember',
                description='Work on 50 completed projects to showcase your SuperMember skills!',
                perks=[f'{badge_xp} XP', 'Recommendation Boost in Recommended Member stack',
                       'SuperMember badge next to your name in all member cards'],
                criteria=50,
                evaluator='n_member_complete'),
            ####################################################################
            ### WellStudied: have total skill_level>=500 across all subjects ###
            Badge(name='WellStudied',
                description='Have a total skill level of 500 across all subjects to showcase your diverse experience!',
                perks=[f'{badge_xp} XP', 'Recommendation Boost for projects with diverse subjects',
                       'WellStudied badge next to your name in all member cards'],
                criteria=500,
                evaluator='total_skill_level'),
            ####################################################################
            ########## Specialist: have skill_level>=50 on any subject #########
            Badge(name='Specialist',
                description='Have a skill level of 50 on one subject to showcase your expertise!',
                perks=[f'{badge_xp} XP', 'Recommendation Boost for projects within your top subject',
                       'Specialist badge next to your name in all member cards',
                       'We will review your profile and connect you with experts in your field'],
                criteria=50,
                evaluator='max_skill_level'),
            ####################################################################
            ########## StarStruck: have earned>=200 cumulative stars ###########
            Badge(name='StarStruck',
                description='Earn a total of 300 stars and cement your superstar-status within the community!',
                perks=[f'{badge_xp} XP',
                    'StarStruck badge next to your name',
                   'We will review your projects and profile our favorite in TheProjectProject social media'],
                criteria=300,
                evaluator='total_stars'),
            ####################################################################
            ########## WellConnected: work with >=100 different people ##########
            Badge(name='WellConnected',
                description='Work with 100 different people to showcase your friendly and sociable nature!',
                perks=[f'{badge_xp} XP', 'WellConnected badge next to your name'],
                criteria=100,
                evaluator='n_unique_members'),
            ####################################################################
            ############ SetEmUp: create >=300 different tasks #################
            Badge(name='SetEmUp',
                description='Create 300 tasks to showcase your delegation skills!',
                perks=[f'{badge_xp} XP', 'SetEmUp badge next to your name'],
                criteria=300,
                evaluator='n_tasks_authored'),
            ####################################################################
            ############ KnockEmDown: complete >=300 different tasks ###########
            Badge(name='KnockEmDown',
                description='Completion 300 tasks to showcase your follow-through!',
                perks=[f'{badge_xp} XP', 'KnockEmDown badge next to your name'],
                criteria=300,
                evaluator='n_tasks_worked'),
            ####################################################################
            ################## Verified: have >=25000 xp #######################
            Badge(name='Verified',
                description='The highest honor any social media user can achieve—the coveted Verified badge!',
                perks=['Verified badge next to your name!',
                       'We will review your account and share your story on TheProjectProject social media',
                       'Recommendation Boost in all Recommendation Stacks'],
                criteria=100000,
                evaluator='get_xp')
            ####################################################################
    ]
    for badge in tqdm(badges):
        db.session.add(badge)
    db.session.commit()
