import os
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text, DateTime, select, Integer
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./sefa.db')
engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase): pass

class Message(Base):
    __tablename__ = 'messages'
    id:        Mapped[int]      = mapped_column(Integer, primary_key=True, autoincrement=True)
    telephone: Mapped[str]      = mapped_column(String(50), index=True)
    role:      Mapped[str]      = mapped_column(String(20))
    content:   Mapped[str]      = mapped_column(Text)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

async def initialiser_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def sauvegarder_message(telephone: str, role: str, content: str):
    async with async_session() as session:
        session.add(Message(telephone=telephone, role=role, content=content, timestamp=datetime.utcnow()))
        await session.commit()

async def obtenir_historique(telephone: str, limite: int = 20) -> list:
    async with async_session() as session:
        q = select(Message).where(Message.telephone == telephone).order_by(Message.timestamp.desc()).limit(limite)
        r = await session.execute(q)
        msgs = list(reversed(r.scalars().all()))
        return [{'role': m.role, 'content': m.content} for m in msgs]

async def effacer_historique(telephone: str):
    async with async_session() as session:
        q = select(Message).where(Message.telephone == telephone)
        r = await session.execute(q)
        for m in r.scalars().all():
            await session.delete(m)
        await session.commit()
