import numpy as np

def get_normed_user_subjects(user, temp):
    # sum raw counts of user subjects
    norm_sum = 0
    for s in user.subjects:
        norm_sum += np.exp(s.number/temp)
    user_subjects = {s.subject : (np.exp(s.number/temp) / norm_sum)
                    for s in user.subjects}
    return user_subjects
