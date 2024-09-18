import sqlalchemy
import sqlalchemy.orm as orm

class Base(orm.DeclarativeBase):
    pass

DBSession = None

def connect():
    global DBSession

    engine = sqlalchemy.create_engine("sqlite:///contacts.sqlite")

    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

    DBSession = orm.sessionmaker(bind=engine)


def get_database():
    if DBSession is None:
        connect()

    db = DBSession()

    try:
        yield db
    finally:
        db.close()