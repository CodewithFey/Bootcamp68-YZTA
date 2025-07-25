from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.cv_parser import parse_cv_for_profile
from app.services.missing_skills import find_missing_skills
from app.services.micro_planning import build_target_prompt, generate_micro_goals

router = APIRouter(prefix="/ai-coach", tags=["AI Kariyer Koçu"])

@router.post("/analyze")
async def analyze_cv(
    cv_file: UploadFile = File(...),
    target_position: str = "ai developer"
):
    # Dosyayı kaydet
    file_location = f"uploads/{cv_file.filename}"
    with open(file_location, "wb") as f:
        f.write(await cv_file.read())

    # CV'den bilgi çek
    cv_data = parse_cv_for_profile(file_location)
    user_skills = cv_data.get("skills", "").split(",")
    missing = find_missing_skills(user_skills, target_position)
    prompt = build_target_prompt(cv_data, target_position)
    micro_goals_and_roadmap = generate_micro_goals(prompt)

    return {
        "profile": cv_data,
        "missing_skills": missing,
        "micro_goals_and_roadmap": micro_goals_and_roadmap
    }
