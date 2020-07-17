import sys
sys.path.append('.')

from application import db
from application.models import Role

import random
def colors(n):
  ret = []
  r = int(random.random() * 256)
  g = int(random.random() * 256)
  b = int(random.random() * 256)
  step = 256 / n
  for i in range(n):
    r += step
    g += step
    b += step
    r = int(r) % 256
    g = int(g) % 256
    b = int(b) % 256
    ret.append((r,g,b))
  return ret


titles = ['Creator',
          'Pending',
          'Full-Stack',
          'Front-End',
          'Back-End',
          'Data Scientist',
          'Software Engineer',
          'Database Engineer',
          'UX/UI',
          'Mobile Developer',
          'Cloud Architect',
          'ML/AI Engineer',
          'Game Developer',
          'Graphic Designer',
          'Security Designer',
          'Other']


def create_roles():
    for t, c in zip(titles, colors(len(titles))):
        db.session.add(Role(t, c))
    db.session.commit()
