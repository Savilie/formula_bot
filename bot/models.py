from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, BigInteger, DateTime

from bot.config.base import Base


class PortfolioItem(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(255), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    phone = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)  # Новое поле
    address = Column(String(255), nullable=False)
    website = Column(String(255), nullable=False)
