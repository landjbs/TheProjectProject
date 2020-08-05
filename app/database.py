from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_


db = SQLAlchemy()


class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, id):
        if any((isinstance(id, str) and id.isdigit(),
                isinstance(id, (int, float))),):
            return cls.query.get(int(id))
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()



def generate_code(name, table):
    ''' Generate unique code for url to access name in table '''
    code = str(name).replace('/', '_').replace(' ', '_').lower()
    temp_code = f'{code}_{str(np.random.randint(0, 1000))}'
    while table.query.filter_by(code=temp_code).first() is not None:
        temp_code = f'{code}_{str(np.random.randint(0, 1000))}'
    return temp_code
