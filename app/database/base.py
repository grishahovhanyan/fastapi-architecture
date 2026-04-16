from datetime import datetime

from sqlalchemy import Integer, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


engine = create_async_engine(settings.database_url)

AsyncSessionLocal = async_sessionmaker(
  engine,
  class_=AsyncSession,
  expire_on_commit=False
)

class Base(DeclarativeBase):
  pass

class IDMixin:
  id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

class TimestampMixin:
  created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
  updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


async def get_db():
  async with AsyncSessionLocal() as session:
    try:
      yield session
      await session.commit()
    except Exception:
      await session.rollback() 
      raise
    finally:
      await session.close()
