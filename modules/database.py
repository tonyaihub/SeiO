import os
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import streamlit as st

Base = declarative_base()

# Получаем URL базы данных:
# 1. Сначала ищем в Streamlit Secrets (для облака)
# 2. Потом в переменных среды
# 3. Если нет — используем локальный SQLite
db_url = st.secrets.get("DATABASE_URL") or os.getenv("DATABASE_URL")

if not db_url:
    # Локальная разработка
    db_url = 'sqlite:///seio_db.sqlite'
    connect_args = {'check_same_thread': False}
else:
    # Продакшн (PostgreSQL)
    # Исправление для SQLAlchemy (postgres:// -> postgresql://)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    connect_args = {}

engine = create_engine(db_url, connect_args=connect_args)
Session = sessionmaker(bind=engine)
session = Session()

class ContentPlan(Base):
    __tablename__ = 'content_plan'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.now)
    topic = Column(String)
    platform = Column(String)
    status = Column(String)
    content_text = Column(Text)
    media_path = Column(String)

class Settings(Base):
    __tablename__ = 'settings'
    key = Column(String, primary_key=True)
    value = Column(String)

# Создаем таблицы, если их нет
Base.metadata.create_all(engine)

def add_plan(date, topic, platform):
    new_post = ContentPlan(date=date, topic=topic, platform=platform, status="Planned")
    session.add(new_post)
    session.commit()

def get_plan():
    # Используем pandas для чтения SQL
    return pd.read_sql(session.query(ContentPlan).statement, session.bind)

def save_setting(key, value):
    # Проверяем, существует ли настройка
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
