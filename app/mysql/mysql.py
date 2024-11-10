import sqlalchemy as db
from app.mysql.base import Base
from sqlalchemy.orm import sessionmaker


class DatabaseClient():
  
  def __init__(self, url: str) -> None:
    engine = db.create_engine(url)
    self.engine = engine
    pass

  def init_database(self):
    """
    creates tables in database
    """
    Base.metadata.create_all(self.engine)
    return
    
