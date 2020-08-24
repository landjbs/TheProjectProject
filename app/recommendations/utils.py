import numpy as np

def get_normed_user_subjects(user, temp):
    # sum raw counts of user subjects
    norm_sum = 0
    user_subjects = []
    for s in user.subjects:
        print('here')
        normed = np.exp(s.number / temp)
        user_subjects.append((s.subject, normed))
        norm_sum += normed
    user_subjects = {s[0] : s[1]/norm_sum for s in user_subjects}
    return user_subjects
