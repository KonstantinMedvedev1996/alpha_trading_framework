from app.db.base import Base
from app.models import security, historicalcandle
from app.db.db import engine



def create_tables():
    engine.echo = True
    # Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    engine.echo = True


def drop_tables():
    engine.echo = True
    Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)
    engine.echo = True