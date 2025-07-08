from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database import get_db
from models import User
import schemas
from utils.hashing import get_password_hash, verify_password
from auth import create_access_token, get_current_user
import os
from typing import Optional

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

@router.put("/profile/complete", response_model=schemas.Message)
def complete_profile(
    profile_data: schemas.ProfileComplete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcının profil bilgilerini tamamlar
    """
    try:
        # Kullanıcı bilgilerini güncelle
        current_user.full_name = profile_data.full_name
        current_user.profession = profile_data.profession
        current_user.experience_level = profile_data.experience_level
        current_user.career_goals = profile_data.career_goals
        current_user.profile_complete = True
        
        db.commit()
        
        return {"message": "Profil başarıyla tamamlandı!"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profil güncelleme sırasında bir hata oluştu"
        )

@router.post("/profile/upload-cv", response_model=schemas.Message)
async def upload_cv(
    cv_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CV dosyası yükler ve profili tamamlar
    """
    try:
        # Dosya formatını kontrol et
        allowed_extensions = ['.pdf', '.doc', '.docx']
        file_extension = os.path.splitext(cv_file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sadece PDF, DOC ve DOCX dosyaları kabul edilir"
            )
        
        # Dosya boyutunu kontrol et (max 10MB)
        if cv_file.size > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dosya boyutu 10MB'dan büyük olamaz"
            )
        
        # Uploads klasörünü oluştur
        upload_dir = "uploads/cvs"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Dosya adını oluştur
        file_name = f"{current_user.username}_{current_user.id}{file_extension}"
        file_path = os.path.join(upload_dir, file_name)
        
        # Dosyayı kaydet
        with open(file_path, "wb") as buffer:
            content = await cv_file.read()
            buffer.write(content)
        
        # Kullanıcı bilgilerini güncelle
        current_user.cv_file_path = file_path
        current_user.profile_complete = True
        
        db.commit()
        
        return {"message": "CV başarıyla yüklendi ve profil tamamlandı!"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CV yükleme sırasında bir hata oluştu"
        )

@router.get("/profile/check-complete")
def check_profile_complete(current_user: User = Depends(get_current_user)):
    """
    Profil tamamlama durumunu kontrol eder
    """
    return {
        "profile_complete": current_user.profile_complete,
        "has_cv": current_user.cv_file_path is not None,
        "has_profile_data": all([
            current_user.full_name,
            current_user.profession,
            current_user.experience_level,
            current_user.career_goals
        ])
    } 