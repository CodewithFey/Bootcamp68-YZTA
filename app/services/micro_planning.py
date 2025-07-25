import google.generativeai as genai


#NOT : CV PARSER İÇİNDEKİ MAİN  İLE BU DOSYA BİRLİKTE KULLANILABİLİR CV_DATA DEĞİŞKENİ CV_PARSER İÇERİSİNDE 
# BULUNMAKTA! EN AŞAĞIDA ÇALIŞTIRMA ÖRNEĞİ BULUNMAKTA


genai.configure(api_key="AIzaSyAGNp5_8h7L-ni5fB536D_xEspUaw_TE9A")

model = genai.GenerativeModel(model_name="gemini-2.5-flash")




def build_target_prompt(cv_data:dict, target_position:str):

    promt = f""" 
    Aşağıda bir adayın özgeçmiş bilgileri ve hedef pozisyonu yer almaktadır.
    Lütfen bu bilgiler doğrultusunda adaya özel mikro hedefler üret.


    // Aday profili\\
    
    {target_position}

    == Yapılacaklar ==

    1. Eksik teknik veya sosyal becerileri madde madde belirt.
    2. Eksik becerileri kapatmak için önerilen eğitimleri ya da içerikleri belirt.
    3. Bu adaya özel bir 3-6 aylık öğrenme planı (haftalık görevlerle) hazırla.
    4. Öğrenme hedeflerini SMART kriterlerine göre öner (Specific, Measurable, Achievable, Relevant, Time-bound).

    """

    return promt.strip()



USE_MOCK = False  # Test sırasında True, gerçek kullanımda False yap

def generate_micro_goals(prompt_text: str) -> str:
    if USE_MOCK:
        return """
        🎯 Mikro Hedefler (Mock Verisi):

        Eksik Beceriler:
        - TensorFlow
        - Docker
        - REST API geliştirme

        Eğitim Önerileri:
        - Coursera: Deep Learning Specialization
        - Udemy: Docker for Developers

        3 Aylık Plan:
        - 1. Hafta: Python tekrar
        - 2. Hafta: NumPy + Pandas
        - 3-4. Hafta: TensorFlow pratikleri
        - ...

        SMART Hedef:
        - 3 ay içinde TensorFlow kullanarak görüntü işleme projesi geliştirmek.
        - Haftalık hedeflerle ilerleyip GitHub’a yüklemek.
        """

    response = model.generate_content(prompt_text)
    return response.text



"""

from cv_parser import main as parse_cv
from mikro_hedef_ai import build_target_prompt, generate_micro_goals

pdf_path = "C:/Users/Yusuf Açık/Desktop/STAJ/S.pdf"

# 1. CV verisini al
cv_data = parse_cv(pdf_path)  # bu bir dict döner

# 2. Prompt oluştur
prompt = build_target_prompt(cv_data, target="AI Developer")

# 3. Gemini'den cevap al
response = generate_micro_goals(prompt)

print(response)




"""