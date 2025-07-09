import re
import spacy
from pdfminer.high_level import extract_text

# İngilizce model yüklü olduğunu varsayıyorum
nlp = spacy.load("en_core_web_sm")

def extract_email(text):
    match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    return match.group() if match else None


#Alanları ayarlama
def split_sections(lines):
    sections = {
        "education": [],
        "experience": [],
        "skills": []
    }
    current_section = None

# Anahtar kelimeleri ayarlama
    edu_keywords = ["education", "eğitim"]
    exp_keywords = ["experience", "work experience", "deneyim"]
    skills_keywords = ["skills", "yetenekler", "beceriler"]

    for line in lines:
        low = line.lower()
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
        if current_section:
            sections[current_section].append(line)

    # Listeyi stringe dönüştür
    for key in sections:
        sections[key] = "\n".join(sections[key]).strip()

    return sections


#Entites göre ayırma kısmı
def extract_entities(text):
    doc = nlp(text)
    entities = []
    for ent in doc.ents:
        entities.append([ent.text, ent.label_])
    return entities


# Satırları listeleme
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

#Test
if __name__ == "__main__":
    pdf_path = r"C:\Users\Yusuf Açık\Desktop\STAJ\ingilizce-cv-ornegi.pdf"
    data = main(pdf_path)

    import json
    print(json.dumps(data, ensure_ascii=False, indent=4))
