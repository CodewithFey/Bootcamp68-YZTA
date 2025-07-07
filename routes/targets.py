from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Target, User
import schemas
from auth import get_current_user

router = APIRouter()

@router.post("/targets", response_model=schemas.TargetOut, status_code=status.HTTP_201_CREATED)
def create_target(
    target: schemas.TargetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Yeni bir kariyer hedefi (şirket ve pozisyon) oluşturur
    """
    try:
        # Yeni hedef oluştur
        db_target = Target(
            user_id=current_user.id,
            company=target.company,
            role=target.role
        )
        
        db.add(db_target)
        db.commit()
        db.refresh(db_target)
        
        return db_target
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hedef oluşturma sırasında bir hata oluştu"
        )

@router.get("/targets", response_model=List[schemas.TargetOut])
def get_my_targets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcının tüm kariyer hedeflerini getirir
    """
    targets = db.query(Target).filter(Target.user_id == current_user.id).all()
    return targets

@router.delete("/targets/{target_id}", response_model=schemas.Message)
def delete_target(
    target_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Kullanıcının belirli bir kariyer hedefini siler
    """
    # Hedefi bul ve kullanıcıya ait olup olmadığını kontrol et
    target = db.query(Target).filter(
        Target.id == target_id,
        Target.user_id == current_user.id
    ).first()
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hedef bulunamadı veya size ait değil"
        )
    
    try:
        db.delete(target)
        db.commit()
        
        return {"message": f"'{target.company}' şirketi için '{target.role}' pozisyonu hedefi başarıyla silindi"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Hedef silme sırasında bir hata oluştu"
        ) 