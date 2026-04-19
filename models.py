from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Note(Base):
    __tablename__ = 'notes'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    
    user = relationship('User', back_populates='notes')
    tags = relationship('Tag', secondary='note_tags')

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    notes = relationship('Note', back_populates='user')

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)

# Настройка подключения
engine = create_engine('postgresql://user:pass@localhost/notes_db')
Session = sessionmaker(bind=engine)