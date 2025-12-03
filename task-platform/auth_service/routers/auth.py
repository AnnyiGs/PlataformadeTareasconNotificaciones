from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from passlib.context import CryptContext

router = APIRouter(prefix="/auth", tags=["Auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    hashed = pwd_context.hash(password)

    user = User(email=email, password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "User created", "id": user.id}


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="Email no encontrado")

    if not pwd_context.verify(password, user.password):
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

    return {"message": "Login correcto", "user_id": user.id}
