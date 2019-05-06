from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from target.settings import DB_NAME, DB_USER, DB_HOST, DB_PASSWORD


class DBBackend(object):
    def __init__(self):
        self._session_factory = None
        self._session = None
        self._engine = create_engine("mysql://{0}:{1}@{2}/{3}?charset=utf8".format(DB_USER, DB_PASSWORD,
                                                                                   DB_HOST, DB_NAME),
                                     pool_recycle=1200,
                                     pool_size=2,
                                     echo=False,
                                     convert_unicode=True,
                                     encoding='utf-8')

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def get_session(self):
        self._session_factory = scoped_session(sessionmaker(bind=self._engine))
        self._session = self._session_factory()
        return self._session

    def get_engine(self):
        return self._engine
