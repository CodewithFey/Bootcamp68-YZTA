from passlib.context import CryptContext

# Bcrypt context oluştur
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """
    Şifreyi bcrypt ile hash'ler
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Düz şifre ile hash'lenmiş şifreyi karşılaştırır
    """
    return pwd_context.verify(plain_password, hashed_password) 