from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class Query(Base):
    __tablename__ = 'queries'

    id = Column(Integer, primary_key=True)
    address = Column(String(34))
