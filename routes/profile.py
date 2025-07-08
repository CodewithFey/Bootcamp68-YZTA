from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserProfileOut, UserProfileUpdate, Message
from auth import get_current_user

router = APIRouter(
    prefix="/me",
    tags=["Profil Yönetimi"]
)

@router.get("/profile", response_model=UserProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mevcut kullanıcının profil bilgilerini getirir
    """
    return current_user

@router.put("/profile", response_model=UserProfileOut)
def update_profile(
    profile_update: UserProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mevcut kullanıcının profil bilgilerini günceller
    """
    # Sadece gönderilen alanları güncelle
    update_data = profile_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        if hasattr(current_user, field):
            setattr(current_user, field, value)
    
    try:
        db.commit()
        db.refresh(current_user)
        return current_user
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profil güncellenirken bir hata oluştu"
        ) 