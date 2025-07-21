from pydantic import BaseModel, Field
from datetime import datetime

# Hedef yönetimi şemaları
class TargetBase(BaseModel):
    company: str = Field(..., min_length=2, max_length=100, description="Şirket adı")
    role: str = Field(..., min_length=2, max_length=100, description="Hedef pozisyon")

class TargetCreate(TargetBase):
    pass

class TargetOut(TargetBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 