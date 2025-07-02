import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import text
from bot.database import engine


def upgrade():
    with engine.connect() as conn:
        try:
            conn.execute(text("""
                ALTER TABLE contacts 
                ADD COLUMN email VARCHAR(100) NOT NULL DEFAULT 'contact@example.com'
            """))
            conn.commit()
            print("✅ Миграция успешно применена")
        except Exception as e:
            print(f"❌ Ошибка миграции: {e}")
            conn.rollback()


if __name__ == "__main__":
    upgrade()