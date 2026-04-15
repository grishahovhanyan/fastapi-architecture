from typing import Generic, TypeVar, Type, Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.base import Base

ModelT = TypeVar("ModelT", bound=Base)

class BaseRepository(Generic[ModelT]):
  def __init__(self, model: Type[ModelT], session: AsyncSession):
    self.model = model
    self.session = session

  async def get_by_id(self, id: int) -> ModelT | None:
    result = await self.session.execute(
      select(self.model).where(self.model.id == id)
    )
    return result.scalar_one_or_none()

  async def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelT]:
    result = await self.session.execute(
      select(self.model).offset(skip).limit(limit)
    )
    return result.scalars().all()

  async def create(self, obj: ModelT) -> ModelT:
    self.session.add(obj)
    await self.session.flush()

    return obj
  
  async def update(self, obj: ModelT, data: dict) -> ModelT:
    for key, value in data.items():
      setattr(obj, key, value)

    await self.session.flush()

    return obj

  async def delete(self, obj: ModelT) -> None:
    await self.session.delete(obj)
