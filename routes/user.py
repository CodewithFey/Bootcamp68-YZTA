from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User
import schemas
from utils.hashing import get_password_hash, verify_password
from auth import create_access_token, get_current_user

router = APIRouter()

@router.post("/register", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Kariyer koçluğu platformuna yeni kullanıcı kaydı
    """
    try:
        # Şifreyi hash'le
        hashed_password = get_password_hash(user.password)
        
        # Yeni kullanıcı oluştur
        db_user = User(
            email=user.email,
            username=user.username,
            password=hashed_password,
            full_name=user.full_name,
            profession=user.profession,
            experience_level=user.experience_level,
            career_goals=user.career_goals
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return {"message": "Kariyer koçluğu platformuna başarıyla kaydoldunuz! Kariyerinizi geliştirmeye hazır mısınız?"}
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bu email veya kullanıcı adı zaten kullanımda"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Kayıt işlemi sırasında bir hata oluştu"
        )

@router.post("/login", response_model=schemas.Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Kariyer koçluğu platformuna giriş ve JWT token üretimi
    """
    # Kullanıcıyı veritabanından bul
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Kullanıcı var mı ve şifre doğru mu kontrol et
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı kullanıcı adı veya şifre",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Access token oluştur
    access_token = create_access_token(data={"sub": user.username})
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }



@router.get("/me", response_model=schemas.UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Mevcut kullanıcının profil bilgilerini ve kariyer bilgilerini döner
    """
    return current_user 