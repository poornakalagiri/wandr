from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# ── PostgreSQL (relational data: users, saved trips, reviews) ──
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://wandr:wandr123@localhost:5432/wandrdb")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── MongoDB (flexible data: destinations, attractions, itineraries) ──
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB  = os.getenv("MONGODB_DB", "wandrdb")

mongo_client = AsyncIOMotorClient(MONGODB_URL)
mongodb = mongo_client[MONGODB_DB]

def get_mongo():
    return mongodb
