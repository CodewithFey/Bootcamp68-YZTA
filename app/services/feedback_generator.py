import google.generativeai as genai

genai.configure(api_key="AIzaSyAGNp5_8h7L-ni5fB536D_xEspUaw_TE9A")

model = genai.GenerativeModel(model_name="gemini-2.5-flash")

def build_feedback_promt(user_task :str, task_description:str):
    prompt = f"""
    
    Aşağıda bir kullanıcının yaptığı görev bulunmaktadır.

    Lütfen görevi değerlendirerek detaylı ve geliştirici geri bildirim ver:
    1. Neleri iyi yapmış?
    2. Hangi kısımlar geliştirilebilir?
    3. Daha iyi olması için somut öneriler ver.
    4. Bu görevi geliştirerek bir üst seviyeye taşıyacak ipuçları yaz.
    5. Eğer gerekliyse kaynak öner (link verme sadece isim olarak belirt).

    == Görev Tanımı ==
    {task_description}

    == Kullanıcının Görevi ==
    {user_task}
    """



def generate_feedback(prompt: str) -> str:
    response = model.generate_content(prompt)
    return response.text    