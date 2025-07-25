import google.generativeai as genai
import numpy as np

# API bağlantısı
genai.configure(api_key="AIzaSyAGNp5_8h7L-ni5fB536D_xEspUaw_TE9A")

# Modelleri başlat
model = genai.GenerativeModel( model="gemini-2.5-flash")
embedding_model = genai.EmbeddingModel(model_name="models/embedding-001")

# ---------------------------------------------------------
def build_profile_text(cv_data: dict) -> str:
    email = cv_data.get("email", "")
    education = cv_data.get("education", "")
    experience = cv_data.get("experience", "")
    skills = cv_data.get("skills", "")
    entities = cv_data.get("entities", [])

    entity_str = "\n".join([f"- {text} ({label})" for text, label in entities])

    profile_text = f"""
📄 AI Aday Profil Özeti
========================

📧 Email: {email}

🎓 Eğitim:
{education}

💼 Deneyim:
{experience}

🛠️ Beceriler:
{skills}

🧠 NLP ile Çekilen Önemli Varlıklar:
{entity_str}
    """

    return profile_text.strip()




# ---------------------------------------------------------
def send_to_gemini(profile_text: str) -> str:
    prompt = f"""
Aşağıda bir adayın özgeçmişine dair bilgiler yer almaktadır.
Bu bilgileri yazılım alanına analiz ederek şu sorulara madde madde cevap ver:

1. Adayın güçlü olduğu teknolojiler, yazılım dilleri ve sosyal yetenekleri nelerdir?
2. Eksik olan ama hedeflediği pozisyon için gerekli beceriler neler olabilir?
3. Bu adaya kariyer gelişimi için önerebileceğin eğitimler nelerdir?
4. Listeli ve düzgün olsun.

=== CV Bilgisi ===
{profile_text}
==================
"""
    response = model.generate_content(prompt)
    return response.text

# ---------------------------------------------------------


def get_profile_embedding(profile_text: str) -> np.ndarray:
    response = embedding_model.embed_content(content=profile_text)
    return np.array(response["embedding"])
