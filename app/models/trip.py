from sqlalchemy import Column, Date, Integer, String
from app.db import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key = True, index = True)
    title = Column(String, nullable = False)
    destination = Column(String, nullable = True)
    start_date = Column(Date, nullable = True)
    end_date = Column(Date, nullable = True)
    status = Column(String, nullable = False, default = "planning")
