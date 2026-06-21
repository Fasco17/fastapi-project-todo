from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.repository import users as users_repository
from app.schemas import UserRequest, UserResponse


def create_user(db: Session, payload: UserRequest) -> UserResponse:
    if users_repository.get_user(db, payload.login):
        raise HTTPException(status_code=400, detail="User already exists")
    user = users_repository.create_user(db, payload.login)
    db.commit()
    return UserResponse.model_validate(user)