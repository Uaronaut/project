# models.py
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

Base = declarative_base()

class Note(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    created_at = Column(String(50))
    updated_at = Column(String(50))

# Функция для получения сессии (если используете SQLAlchemy)
def get_session():
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///notes.db')
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)  # создаёт таблицу, если её нет
    Session = sessionmaker(bind=engine)
    return Session()