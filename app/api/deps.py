from typing import Generator

from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.user_service import UserService


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)