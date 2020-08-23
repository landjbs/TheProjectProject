import json

from app.database import db, CRUDMixin


class JSONField(db.TextField):
    ''' Store json data from analytics as text '''
    def python_value(self, value):
        if value is not None:
            return json.loads(value)

    def db_value(self, value):
        if value is not None:
            return json.dumps(value)


class PageView(CRUDMixin, db.Model):
    pass
