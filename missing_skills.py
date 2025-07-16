from job_roles import job_requirements





def normalize_skills(skills):


    """
    Becerileri küçük harfe çevirip boşlukları kırpar.
    """

    return set(skill.lower() for skill in skills)


def find_missing_skills(cv_skills,target_position):

    """
    Hedef pozisyona göre eksik becerileri belirler.
    """

    position = target_position.lower().strip()


    if position not in job_requirements:
        raise ValueError(f"Hedef pozisyon '{target_position}' tanımlı değil. job_roles.py dosyasını kontrol et.")

    requirement_skills = normalize_skills(job_requirements[position])
    user_skills = normalize_skills(cv_skills)

    missing_skills = sorted(list(requirement_skills-user_skills))

    return missing_skills

