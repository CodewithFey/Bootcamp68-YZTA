from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

# Kullanıcı kayıt şeması
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, description="Kullanıcı adı")
    password: str = Field(..., min_length=6, description="Şifre (minimum 6 karakter)")
    full_name: Optional[str] = Field(None, description="Tam ad")
    profession: Optional[str] = Field(None, description="Meslek/İş alanı")
    experience_level: Optional[str] = Field(None, description="Deneyim seviyesi (Başlangıç/Orta/İleri)")
    career_goals: Optional[str] = Field(None, description="Kariyer hedefleri")

# Kullanıcı giriş şeması
class UserLogin(BaseModel):
    username: str
    password: str

# Kullanıcı yanıt şeması (şifre olmadan)
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    profession: Optional[str] = None
    experience_level: Optional[str] = None
    career_goals: Optional[str] = None
    profile_complete: Optional[bool] = None
    cv_file_path: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Kullanıcı güncelleme şeması
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    profession: Optional[str] = None
    experience_level: Optional[str] = None
    career_goals: Optional[str] = None

# Profil tamamlama şeması
class ProfileComplete(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100, description="Tam ad")
    profession: str = Field(..., min_length=2, max_length=100, description="Meslek")
    experience_level: str = Field(..., description="Deneyim seviyesi")
    career_goals: str = Field(..., min_length=10, description="Kariyer hedefleri")

# Profil yönetimi şemaları
class UserProfileOut(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    profession: Optional[str] = None
    experience_level: Optional[str] = None
    career_goals: Optional[str] = None
    skills: Optional[str] = None
    interests: Optional[str] = None
    education_level: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, description="Tam ad")
    profession: Optional[str] = Field(None, description="Meslek/İş alanı")
    experience_level: Optional[str] = Field(None, description="Deneyim seviyesi")
    career_goals: Optional[str] = Field(None, description="Kariyer hedefleri")
    skills: Optional[str] = Field(None, description="Beceriler")
    interests: Optional[str] = Field(None, description="İlgi alanları")
    education_level: Optional[str] = Field(None, description="Eğitim seviyesi") 