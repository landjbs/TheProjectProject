from app.database import db, CRUDMixin


## BASE CLASSES ##
class Badge(CRUDMixin, db.Model):
    __tablename__ = 'badge'
    # id
    id = db.Column(db.Integer, primary_key=True)
    # name
    name = db.Column(db.String(60), nullable=False, unique=True)
    # url for icon
    icon_url = db.Column(db.String(250), nullable=False, unique=True)
    # color
    color = db.Column(db.String(6), unique=True, nullable=False)
    # users
    users = relationship('User_Badge', back_populates='badge', lazy='dynamic')

    def __repr__(self):
        return f'<Badge {self.name}>'
