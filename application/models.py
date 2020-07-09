from application import db


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True, unique=False, info={'label':'Password'})
    email = db.Column(db.String(254), unique=False, nullable=False,
                      info={'label':'Email Address'})
    # password
    password = Column(String(254), nullable=False, info={'label':'Password'})

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def __repr__(self):
        return '<User %r>' % self.name
