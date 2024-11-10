from sqlalchemy import Column, Integer, String, Sequence
from app.mysql.base import Base


class User(Base):
  __tablename__ = "users"
  id = Column(Integer, Sequence("user_id_seq"), primary_key=True)
  name = Column(String(50))
  fullname = Column(String(50))
  age = Column(Integer)

  def __repr__(self) -> str:
    return "<User(id= '%d', name='%s', fullname='%s', age='%d')>" % (
      self.id,
      self.name,
      self.fullname,
      self.age,
    )