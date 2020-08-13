'''
Possible question ideas for project. Eventually maybe expand to be project-taylored
questions but that's way later.
'''

import numpy as np


question_suggestions = [
    ########### INSPIRATION: How you came up with idea #########################
    'How did you come up with this idea?',
    "What is your team's experience in this field?",
    ############################################################################
    ############## SO FAR: How the process is going ############################
    'What is the most difficult challenge you have faced so far?',
    'What have you learned through your work on this project so far?',
    'What have you completed so far?',
    ############################################################################
    ############## GOING FOWARD: What is left to do ############################
    'What is left to do?',
    'What is your end goal for this project?',
    ############################################################################
    ######## TEAM DESIRES: What are you looking for in a team ##################
    'What are you looking for in a team?',
    'How much time should members expect to commit each day?'
    ############################################################################
]

question_num = len(question_suggestions)


def suggest_questions(project):
    return [question for question in question_suggestions
            if not project.questions.filter_by(question=question).first()]



def choose_init_questions(project, n=8):
    if n>question_num:
        print(f'WARNING: n {n} is greater than max questions {question_num}.')
        n = question_num
    q_ids = np.random.choice(range(question_num), size=n, replace=False)
    return [question_suggestions[id] for id in q_ids]
