import re
import os
from pdfminer.high_level import extract_text

# Spacy'yi isteğe bağlı olarak import et
try:
    import spacy
    nlp = spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    print("Spacy modülü bulunamadı. Temel metin işleme kullanılacak.")
    SPACY_AVAILABLE = False
    nlp = None

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else None

def extract_name(text, entities=None):
    """CV'den kişi ismini çıkart"""
    # Eğer spacy entities varsa önce onu kullan
    if entities and SPACY_AVAILABLE:
        names = [ent[0] for ent in entities if ent[1] == "PERSON"]
        if names:
            return max(names, key=len)
    
    # Spacy yoksa veya entities bulamazsa, metnin başından isim aramaya çalış
    lines = text.split('\n')[:15]  # İlk 15 satır
    for line in lines:
        line = line.strip()
        # Basit isim kontrolü: 2-4 kelime, her kelime büyük harfle başlıyor
        words = line.split()
        if 2 <= len(words) <= 4 and all(word[0].isupper() and word.isalpha() for word in words):
            # Email, telefon veya sayı içermiyorsa isim olabilir
            if not re.search(r'[@\d().-]', line) and len(line) > 5:
                return line
    
    # CV başlığından isim çıkarmaya çalış
    cv_patterns = [
        r'^([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'CV\s*-?\s*([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)',
        r'Resume\s*-?\s*([A-Z][a-z]+ [A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
    ]
    
    for pattern in cv_patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            return match.group(1)
    
    return None

def extract_profession(text):
    """CV'den mesleği çıkart"""
    # Yaygın meslek unvanları
    job_titles = [
        "software engineer", "yazılım mühendisi", "developer", "geliştirici",
        "data scientist", "veri bilimci", "analyst", "analist", 
        "manager", "müdür", "coordinator", "koordinatör",
        "specialist", "uzman", "consultant", "danışman",
        "designer", "tasarımcı", "architect", "mimar",
        "engineer", "mühendis", "technician", "teknisyen",
        "teacher", "öğretmen", "instructor", "eğitmen",
        "nurse", "hemşire", "doctor", "doktor",
        "lawyer", "avukat", "accountant", "muhasebeci",
        "product manager", "ürün müdürü", "project manager", "proje yöneticisi",
        "business analyst", "iş analisti", "quality assurance", "kalite güvence",
        "devops engineer", "devops mühendisi", "frontend developer", "frontend geliştirici",
        "backend developer", "backend geliştirici", "full stack developer", "full stack geliştirici"
    ]
    
    text_lower = text.lower()
    found_titles = []
    
    for title in job_titles:
        if title in text_lower:
            # Başlık etrafındaki konteksti al
            pattern = r'(?:^|\s)([^.\n]*' + re.escape(title) + r'[^.\n]*)(?:\.|$|\n)'
            matches = re.findall(pattern, text_lower, re.MULTILINE)
            if matches:
                # En uygun olanı seç (en kısa ve temiz olan)
                for match in matches:
                    clean_match = match.strip()
                    if 5 <= len(clean_match) <= 50:  # Makul uzunlukta
                        found_titles.append(clean_match)
    
    if found_titles:
        # En kısa ve en uygun olanı seç
        return min(found_titles, key=len).strip().title()
    
    return None

def extract_experience_level(text):
    """CV'den deneyim seviyesini çıkart"""
    text_lower = text.lower()
    
    # Yıl bazında deneyim arama
    year_patterns = [
        r'(\d+)\s*(?:yıl|year|years|yıllık)?\s*(?:deneyim|experience)',
        r'(?:deneyim|experience).*?(\d+)\s*(?:yıl|year|years)',
        r'(\d+)\+?\s*(?:year|years|yıl)\s*(?:of\s*)?(?:experience|deneyim)',
        r'(\d+)\s*(?:years?|yıl)\s*(?:of\s*)?(?:professional\s*)?(?:experience|deneyim)'
    ]
    
    years = []
    for pattern in year_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            try:
                year_val = int(match)
                if 0 <= year_val <= 50:  # Makul yıl aralığı
                    years.append(year_val)
            except ValueError:
                continue
    
    if years:
        max_years = max(years)
        if max_years <= 2:
            return "Başlangıç"
        elif max_years <= 5:
            return "Orta"
        elif max_years <= 10:
            return "İleri"
        else:
            return "Uzman"
    
    # Anahtar kelimelerle seviye belirleme
    if any(word in text_lower for word in ["junior", "başlangıç", "entry level", "fresher", "graduate", "yeni mezun"]):
        return "Başlangıç"
    elif any(word in text_lower for word in ["senior", "lead", "principal", "uzman", "expert", "architect", "chief"]):
        return "İleri"
    elif any(word in text_lower for word in ["mid", "intermediate", "orta seviye", "mid-level"]):
        return "Orta"
    
    return None

def extract_education_level(text):
    """CV'den eğitim seviyesini çıkart"""
    text_lower = text.lower()
    
    # Eğitim seviyesi anahtar kelimeleri (öncelik sırasına göre)
    education_levels = [
        ("Doktora", ["phd", "ph.d", "doctorate", "doktora", "doctoral", "doktor"]),
        ("Yüksek Lisans", ["master", "msc", "ma", "mba", "yüksek lisans", "graduate degree", "masters"]),
        ("Lisans", ["bachelor", "bs", "ba", "lisans", "undergraduate", "üniversite", "university degree"]),
        ("Önlisans", ["associate", "önlisans", "meslek yüksekokulu", "associate degree"]),
        ("Lise", ["high school", "lise", "secondary", "secondary school", "diploma"])
    ]
    
    for level, keywords in education_levels:
        if any(keyword in text_lower for keyword in keywords):
            return level
    
    return None

#Alanları ayarlama
def split_sections(lines):
    sections = {
        "education": [],
        "experience": [],
        "skills": []
    }
    current_section = None

# Anahtar kelimeleri ayarlama
    edu_keywords = ["education", "eğitim", "öğrenim", "educational background"]
    exp_keywords = ["experience", "work experience", "deneyim", "iş deneyimi", "work history", "professional experience"]
    skills_keywords = ["skills", "yetenekler", "beceriler", "technical skills", "teknik beceriler"]

    for line in lines:
        low = line.lower().strip()
        if any(k in low for k in edu_keywords):
            current_section = "education"
            continue
        elif any(k in low for k in exp_keywords):
            current_section = "experience"
            continue
        elif any(k in low for k in skills_keywords):
            current_section = "skills"
            continue

        # Eğer bir bölüm aktifse satırları oraya ekle
        if current_section and line.strip():
            sections[current_section].append(line)

    # Listeyi stringe dönüştür
    for key in sections:
        sections[key] = "\n".join(sections[key]).strip()

    return sections

#Entites göre ayırma kısmı
def extract_entities(text):
    """Spacy kullanılabilirse entities çıkart, değilse boş liste döndür"""
    if not SPACY_AVAILABLE or not nlp:
        return []
    
    try:
        doc = nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append([ent.text, ent.label_])
        return entities
    except Exception as e:
        print(f"Entity extraction hatası: {e}")
        return []

def parse_cv_for_profile(file_path):
    """CV dosyasını işleyerek profil bilgilerini çıkart"""
    try:
        # PDF'den metin çıkart
        text = extract_text(file_path)
        if not text or len(text.strip()) < 50:
            print("CV'den yeterli metin çıkarılamadı")
            return {}
        
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Bölümlerine ayır
        sections = split_sections(lines)
        
        # Varlıkları çıkart (spacy varsa)
        entities = extract_entities(text) if SPACY_AVAILABLE else []
        
        # Profil bilgilerini çıkart
        profile_data = {
            "full_name": extract_name(text, entities),
            "email": extract_email(text),
            "profession": extract_profession(text),
            "experience_level": extract_experience_level(text),
            "education_level": extract_education_level(text),
            "skills": sections.get("skills", ""),
            "education_info": sections.get("education", ""),
            "experience_info": sections.get("experience", ""),
        }
        
        # Debug için
        print(f"CV işleme sonucu: {profile_data}")
        
        # Boş değerleri temizle
        cleaned_data = {}
        for key, value in profile_data.items():
            if value and str(value).strip() and str(value).strip() != "":
                cleaned_data[key] = str(value).strip()
        
        return cleaned_data
        
    except Exception as e:
        print(f"CV işleme hatası: {e}")
        return {}

# Eski fonksiyonlar (geriye uyumluluk için)
def main(pdf_path):
    text = extract_text(pdf_path)
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    sections = split_sections(lines)
    email = extract_email(text)
    entities = extract_entities(text)

    final_data = {
        "email": email if email else "",
        "education": sections.get("education", ""),
        "experience": sections.get("experience", ""),
        "skills": sections.get("skills", ""),
        "entities": entities
    }

    return final_data

def clean_skill_text(skill_text):
    # Virgülle veya yeni satırla ayrılmış becerileri ayıkla
    skills = re.split(r"[,\n]", skill_text)
    return [s.strip().lower() for s in skills if s.strip()]

#Test
if __name__ == "__main__":
    pdf_path = r"C:\Users\Yusuf Açık\Desktop\STAJ\S.pdf"
    if os.path.exists(pdf_path):
        data = main(pdf_path)
        
        # Test kısmı 
        cv_skills = data["skills"]
        clean_skils = clean_skill_text(cv_skills)
        target = "ai developer"
        
        try:
            from app.services.missing_skills import find_missing_skills
            missing = find_missing_skills(clean_skils, target)
            print("Eksik beceriler:", missing)
        except ImportError:
            print("Missing skills modülü bulunamadı")
    else:
        print("Test PDF dosyası bulunamadı")