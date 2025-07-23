import requests
from cv_parser import main  # CV verisini çıkaran fonksiyonu import ediyoruz

# PDF yolunu belirt
pdf_path = r"C:\Users\Yusuf Açık\Desktop\STAJ\S.pdf"

# CV verisini al
cv_data = main(pdf_path)

# FastAPI adresini belirt
api_url = "http://localhost:8000/api/cv/analyze" #örnek olarak!!!!

# API’ye JSON olarak POST isteği gönder
response = requests.post(api_url, json=cv_data)

# Sonucu yazdır
if response.status_code == 200:
    print("✅ API'den gelen cevap:")
    print(response.json())
else:
    print(f"❌ Hata kodu: {response.status_code}")
    print(response.text)
