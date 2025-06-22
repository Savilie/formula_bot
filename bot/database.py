from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bot.config.settings import settings

from bot.config.base import Base
from bot.models import Contact


# Формат подключения: mysql+mysqlconnector://user:password@host:port/dbname
SQLALCHEMY_DATABASE_URL = (
    f"mysql+mysqlconnector://{settings.DB_USER}:{settings.DB_PASS}@"
    f"{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)

    # Добавляем пустые контакты при первом запуске
    db = SessionLocal()
    try:
        if not db.query(Contact).first():
            default_contacts = Contact(
                phone="+7 (XXX) XXX-XX-XX",
                address="Город, Улица, Дом",
                website="https://example.com"
            )
            db.add(default_contacts)
            db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
