from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Target(Base):
    __tablename__ = "targets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company = Column(String, nullable=False)  # Şirket adı
    role = Column(String, nullable=False)  # Hedef pozisyon
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Kullanıcı ilişkisi
    user = relationship("User", back_populates="targets")
    
    def __repr__(self):
        return f"<Target(id={self.id}, user_id={self.user_id}, company='{self.company}', role='{self.role}')>" 