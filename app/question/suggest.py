'''
Possible question ideas for project. Eventually maybe expand to be project-taylored
questions but that's way later.
'''

import numpy as np


question_suggestions = [
    ########### INSPIRATION: How you came up with idea #########################
    'How did you come up with this idea?',
    ############################################################################
    ############## SO FAR: How the process is going ############################
    'What is the most difficult challenge you have faced?',
    'What have you learned through your work on this project?'
    ############################################################################
]

question_num = len(question_suggestions)


def suggest_questions(project):
    return [question for question in question_suggestions
            if not project.questions.filter_by(question=question).first()]



def choose_init_questions(project, n=3):
    if n>question_num:
        raise ValueError(f'n {n} is greater than max questions {question_num}.')
    q_ids = np.random.randint(0, question_num+1, size=n)
    return set()
