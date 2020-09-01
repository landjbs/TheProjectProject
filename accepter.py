from time import time

from app.user.models import User

while True:
    time.sleep(30)
    pending = User.query.filter_by(confirmed=True, accepted=False)
    for user in pending:
        user.accept()
        print(f'ACCEPTED: {user.name}.')
