from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User
from app.schemas import UserProfileOut, UserProfileUpdate, Message, ProfileComplete
from app.core.auth import get_current_user
from app.services.cv_parser import parse_cv_for_profile
import os
from typing import Optional

router = APIRouter(
    prefix="/profile",
    tags=["Profil Yönetimi"]
)

@router.get("/me", response_model=UserProfileOut)
def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mevcut kullanıcının profil bilgilerini getirir
    """
    return current_user

@router.put("/me", response_model=UserProfileOut)
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

@router.put("/complete", response_model=Message)
def complete_profile(
    profile_data: ProfileComplete,
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

@router.post("/upload-cv", response_model=Message)
async def upload_cv(
    cv_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    CV dosyası yükler, işler ve profili otomatik olarak tamamlar
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
        
        # CV dosya yolunu kaydet
        current_user.cv_file_path = file_path
        
        # CV'yi işle ve profil bilgilerini çıkart (sadece PDF destekleniyor şimdilik)
        profile_updates = {}
        if file_extension == '.pdf':
            try:
                cv_data = parse_cv_for_profile(file_path)
                
                # CV'den çıkarılan bilgileri kullanıcı profiline uygula
                # Sadece boş olan alanları doldur
                if cv_data.get('full_name') and not current_user.full_name:
                    profile_updates['full_name'] = cv_data['full_name']
                    current_user.full_name = cv_data['full_name']
                
                if cv_data.get('profession') and not current_user.profession:
                    profile_updates['profession'] = cv_data['profession']
                    current_user.profession = cv_data['profession']
                
                if cv_data.get('experience_level') and not current_user.experience_level:
                    profile_updates['experience_level'] = cv_data['experience_level']
                    current_user.experience_level = cv_data['experience_level']
                
                if cv_data.get('education_level') and not current_user.education_level:
                    profile_updates['education_level'] = cv_data['education_level']
                    current_user.education_level = cv_data['education_level']
                
                if cv_data.get('skills') and not current_user.skills:
                    profile_updates['skills'] = cv_data['skills']
                    current_user.skills = cv_data['skills']
                
            except Exception as e:
                print(f"CV işleme hatası: {e}")
                # CV işleme başarısız olsa bile dosya yükleme devam etsin
        
        db.commit()
        
        # Sonuç mesajını oluştur
        if profile_updates:
            updated_fields = list(profile_updates.keys())
            message = f"CV başarıyla yüklendi ve şu bilgiler otomatik olarak dolduruldu: {', '.join(updated_fields)}. "
            message += "Eksik bilgileri tamamlamak için profil düzenleme sayfasını kullanabilirsiniz."
        else:
            message = "CV başarıyla yüklendi! Profil bilgilerinizi kontrol edip eksik olanları tamamlayın."
        
        return {"message": message}
        
    except Exception as e:
        db.rollback()
        print(f"CV yükleme hatası: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CV yükleme sırasında bir hata oluştu"
        )

@router.get("/check-complete")
def check_profile_complete(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Profil tamamlama durumunu kontrol eder
    """
    # CV kontrolü
    has_cv = current_user.cv_file_path is not None and current_user.cv_file_path != ""
    
    # Profil bilgileri kontrolü
    has_profile_data = all([
        current_user.full_name,
        current_user.profession,
        current_user.experience_level,
        current_user.career_goals
    ])
    
    # Hedef kontrolü - kullanıcının en az bir hedefi var mı?
    from app.models import Target
    has_targets = db.query(Target).filter(Target.user_id == current_user.id).count() > 0
    
    # Profil tamamlama yüzdesi hesaplama
    completed_steps = 0
    total_steps = 3
    
    if has_cv or has_profile_data:
        completed_steps += 1  # Profil bilgileri/CV
    if has_targets:
        completed_steps += 1  # Hedefler
    if has_cv and has_profile_data and has_targets:
        completed_steps = 3   # Hepsi tamamlanmış
    
    completion_percentage = round((completed_steps / total_steps) * 100)
    
    # Profil tam tamamlanma kriteri: CV VEYA profil bilgileri + en az bir hedef
    profile_complete = (has_cv or has_profile_data) and has_targets
    
    return {
        "profile_complete": profile_complete,
        "has_cv": has_cv,
        "has_profile_data": has_profile_data,
        "has_targets": has_targets,
        "completion_percentage": completion_percentage,
        "targets_count": db.query(Target).filter(Target.user_id == current_user.id).count(),
        "cv_filename": os.path.basename(current_user.cv_file_path) if has_cv else None,
        "next_step": _get_next_step(has_cv, has_profile_data, has_targets)
    }

def _get_next_step(has_cv: bool, has_profile_data: bool, has_targets: bool) -> str:
    """Kullanıcının bir sonraki adımını belirler"""
    if not (has_cv or has_profile_data):
        return "upload_cv_or_complete_profile"
    elif not has_targets:
        return "set_targets"
    else:
        return "completed" 