# WARNING: deprecated/not used

from time import sleep

from app import app


with app.app_context():
    from app import db
    print('ACCEPTER RUNNING')
    while True:
        sleep(1)
        pending = db.session.query('User').filter_by(confirmed=True, accepted=False)
        for user in pending:
            user.accept()
            print(f'ACCEPTED: {user.name}.')
