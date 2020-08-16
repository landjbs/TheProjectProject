from numpy.random import randint
from flask_sqlalchemy import SQLAlchemy, event
from sqlalchemy import or_

# from app.recommendations.elastic_search import (
#         add_to_index, remove_from_index, query_index
# )


db = SQLAlchemy()


class CRUDMixin(object):
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    __searchable__ = False

    @classmethod
    def get_by_id(cls, id):
        if any((isinstance(id, str) and id.isdigit(),
                isinstance(id, (int, float))),):
            return cls.query.get(int(id))
        return None

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        # TEMP: searching should be moved to SearchableMixin asap
        # if instance.__searchable__:
            # add_to_index(cls.__tablename__, instance)
        return instance.save()

    def update(self, commit=True, **kwargs):
        # TEMP: searching should be moved to SearchableMixin asap
        # if self.__searchable__:
            # remove_from_index(self.__tablename__, self)
            # add_to_index(self.__tablename__, self)
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        db.session.add(self)
        # TEMP: searching should be moved to SearchableMixin asap
        # if self.__searchable__:
            # remove_from_index(self.__tablename__, self)
            # add_to_index(self.__tablename__, self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        # TEMP: searching should be moved to SearchableMixin asap
        # if self.__searchable__:
        #     remove_from_index(self.__tablename__, self)
        db.session.delete(self)
        return commit and db.session.commit()


def generate_code(name, table):
    ''' Generate unique code for url to access name in table '''
    code = str(name).replace('/', '_').replace(' ', '_').lower()
    temp_code = f'{code}_{str(randint(0, 1000))}'
    while table.query.filter_by(code=temp_code).first() is not None:
        temp_code = f'{code}_{str(randint(0, 1000))}'
    return temp_code



# class SearchableMixin(object):
#     __table_args__ = {'extend_existing': True}
#
#     @classmethod
#     def search(cls, expression, page, per_page):
#         ''' Gets list of results as SQLAlchemy instances using Elasticsearch '''
#         ids, total = query_index(cls.__tablename__, expression, page, per_page)
#         if total == 0:
#             return cls.query.filter_by(id=0), 0
#         when = []
#         for i, id in enumerate(ids):
#             when.append((id, i))
#         return cls.query.filter(cls.id.in_(ids)).order_by(
#             db.case(when, value=cls.id)), total
#
#     @classmethod
#     def before_commit(cls, session):
#         ''' Tags changes before commit to update index after '''
#         print("BEFORE")
#         session._changes = {
#             'add': list(session.new),
#             'update': list(session.dirty),
#             'delete': list(session.deleted)
#         }
#
#     @classmethod
#     def after_commit(cls, session):
#         ''' Update search index after commit is successfully completed '''
#         print("AFTER")
#         for obj in session._changes['add']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.__tablename__, obj)
#         for obj in session._changes['update']:
#             if isinstance(obj, SearchableMixin):
#                 add_to_index(obj.__tablename__, obj)
#         for obj in session._changes['delete']:
#             if isinstance(obj, SearchableMixin):
#                 remove_from_index(obj.__tablename__, obj)
#         session._changes = None
#
#     @classmethod
#     def reindex(cls):
#         ''' Rebuilds index using all class data from rds '''
#         for obj in cls.query:
#             add_to_index(cls.__tablename__, obj)
#
#
#
#
# ############## establish handlers for SearchableMixin ##########################
# # @db.event.listens_for(db.session, 'before_commit')
# # def before_commit(SearchableMixin, session):
# #     ''' Tags changes before commit to update index after '''
# #     print("BEFORE")
# #     session._changes = {
# #         'add': list(session.new),
# #         'update': list(session.dirty),
# #         'delete': list(session.deleted)
# #     }
# ################################################################################
