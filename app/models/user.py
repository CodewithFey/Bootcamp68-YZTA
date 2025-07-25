from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    # Kariyer koçluğu için ek alanlar
    profession = Column(String, nullable=True)  # Meslek
    experience_level = Column(String, nullable=True)  # Deneyim seviyesi
    career_goals = Column(Text, nullable=True)  # Kariyer hedefleri
    # Profil yönetimi için ek alanlar
    skills = Column(String, nullable=True)  # Beceriler
    interests = Column(String, nullable=True)  # İlgi alanları
    education_level = Column(String, nullable=True)  # Eğitim seviyesi
    profile_complete = Column(Boolean, default=False)  # Profil tamamlama durumu
    cv_file_path = Column(String, nullable=True)  # CV dosya yolu
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Hedefler ilişkisi
    targets = relationship("Target", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', profession='{self.profession}')>" 