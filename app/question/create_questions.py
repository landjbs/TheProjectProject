from .models import Question

from tqdm import tqdm


def create_badges(db):
    ''' Creates all static questions '''
    badges = [
        ################## INSPIRATIONS: How the project came about ############
        Question(question='How did you get this idea?'),
        Question(question='What is the biggest challenge you have faced?'),
        Question(question='What is the biggest challenge you have faced?'),
    ]
    for question in tqdm(questions):
        db.session.add(question)
    db.session.commit()
