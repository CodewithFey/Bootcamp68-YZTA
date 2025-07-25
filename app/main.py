from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.core.database import engine, Base
from app.api.v1.routes import user, targets, profile
import uvicorn
from app.api.v1.routes import ai_coach  # AI Kariyer
# Veritabanı tablolarını oluştur
Base.metadata.create_all(bind=engine)

# FastAPI uygulaması oluştur
app = FastAPI(
    title="AI Destekli Kariyer Koçu API",
    description="Kişiselleştirilmiş kariyer rehberliği için AI destekli platform",
    version="1.0.0"
)

# CORS middleware ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Üretimde belirli domainlere sınırlandırın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router'ları dahil et
app.include_router(user.router, prefix="/api/v1", tags=["Kullanıcı Yönetimi"])
app.include_router(targets.router, prefix="/api/v1", tags=["Hedef Yönetimi"])
app.include_router(profile.router, prefix="/api/v1", tags=["Profil Yönetimi"])
app.include_router(ai_coach.router, prefix="/api/v1", tags=["AI Kariyer Koçu"])

# Static files için mount (CSS, JS, images vb.)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/templates", StaticFiles(directory="templates"), name="templates")

@app.get("/")
def read_root():
    """
    Ana sayfa - Login sayfasına yönlendir
    """
    return RedirectResponse(url="/templates/login.html")

@app.get("/api")
def api_info():
    """
    API bilgileri endpoint'i
    """
    return {
        "message": "AI Destekli Kariyer Koçu API'sine hoş geldiniz!",
        "description": "Kişiselleştirilmiş kariyer rehberliği için AI destekli platform",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    """
    Sağlık kontrolü endpoint'i
    """
    return {"status": "healthy", "message": "Kariyer Koçu API çalışıyor"}




# Server başlatma artık start_server.py ile yapılıyor
# Doğrudan uvicorn komutları ile de çalıştırılabilir 