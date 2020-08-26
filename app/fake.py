import numpy as np
from faker import Faker

from app.subject.models import Subject
from app.badge.models import Badge


fake = Faker()

# cache database specs
subject_num = None
badge_num = None


def rand_words(n):
    return ' '.join([fake.word() for _ in range(n)])


def rand_bool(p_true):
    return np.random.choice([True, False], p=[p_true, (1-p_true)])


def rand_subjects(n):
    global subject_num
    if subject_num is None:
        subject_num = Subject.query.count()
    return [Subject.get_by_id(int(id))
            for id in np.random.randint(1, subject_num+1, size=n)]

def rand_badges(n):
    global badge_num
    if badge_num is None:
        badge_num = Badge.query.count()
    if n==0:
        return []
    return [Badge.get_by_id(int(id))
            for id in np.random.randint(1, badge_num+1, size=n)]
