import sqlite3
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

Base = declarative_base()
engine = create_engine('sqlite:///seio_db.sqlite', connect_args={'check_same_thread': False})
Session = sessionmaker(bind=engine)
session = Session()

class ContentPlan(Base):
    __tablename__ = 'content_plan'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    topic = Column(String)
    platform = Column(String)
    status = Column(String) # Planned, Generated, Posted
    content_text = Column(Text)
    media_path = Column(String)

class Settings(Base):
    __tablename__ = 'settings'
    key = Column(String, primary_key=True)
    value = Column(String)

Base.metadata.create_all(engine)

def add_plan(date, topic, platform):
    new_post = ContentPlan(date=date, topic=topic, platform=platform, status="Planned")
    session.add(new_post)
    session.commit()

def get_plan():
    return pd.read_sql(session.query(ContentPlan).statement, session.bind)

def save_setting(key, value):
    setting = session.query(Settings).filter_by(key=key).first()
    if setting:
        setting.value = value
    else:
        setting = Settings(key=key, value=value)
        session.add(setting)
    session.commit()

def get_setting(key):
    setting = session.query(Settings).filter_by(key=key).first()
    return setting.value if setting else None
