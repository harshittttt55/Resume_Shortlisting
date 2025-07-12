import os
import re
import pdfplumber
import spacy
import pandas as pd
from datetime import datetime

nlp = spacy.load("en_core_web_lg")

year_pattern = re.compile(
    r"(?P<years>\d+(?:\.\d+)?)(?:\+|-)?\s*(?:years?|yrs?\.?)?\s*(?:of\s*)?experience|"
    r"(?P<start_month>[a-zA-Z]{3,9})?\s*(?P<start_year>\d{4})\s*[-to]+\s*"
    r"(?P<end_month>[a-zA-Z]{3,9})?\s*(?P<end_year>\d{4})\s*(?:experience)?",
    re.IGNORECASE
)

def pdfextract(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def extract_years_of_experience(resume_text):
    total_years = 0.0
    for match in year_pattern.finditer(resume_text):
        if match.group("years"):
            total_years += float(match.group("years"))
        elif match.group("start_year") and match.group("end_year"):
            try:
                start_month = match.group("start_month") or "Jan"
                end_month = match.group("end_month") or "Dec"
                start_date = datetime.strptime(f"{start_month[:3]} {match.group('start_year')}", "%b %Y")
                end_date = datetime.strptime(f"{end_month[:3]} {match.group('end_year')}", "%b %Y")
                difference_in_years = (end_date - start_date).days / 365.25
                total_years += difference_in_years
            except ValueError:
                continue
    return total_years

def match_experience(years_of_experience, experience_map):
    for (min_years, max_years), score in experience_map.items():
        if min_years <= years_of_experience < max_years:
            return score
    return 0

def load_job_skills(csv_path):
    job_skills = {}
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        title = row["Job Title"].strip()
        skills = [skill.strip().lower() for skill in row["Skills"].split(",") if skill.strip()]
        job_skills[title] = skills
    return job_skills

def extract_skills_from_resume(resume_text, all_skills):
    resume_text_lower = resume_text.lower()
    matched_skills = set()
    for skill in all_skills:
        if skill in resume_text_lower:
            matched_skills.add(skill)
    return matched_skills

def score_against_job(matched_skills, required_skills):
    return len(matched_skills.intersection(required_skills))

def rank_resumes_against_job(job_title, resume_folder, job_skills_csv):
    job_skills_map = load_job_skills(job_skills_csv)
    required_skills = set(job_skills_map.get(job_title, []))

    if not required_skills:
        raise ValueError(f"No skills found for job title: {job_title}")

    all_skills = set(skill for skills in job_skills_map.values() for skill in skills)
    resume_scores = []

    pdf_files = find_pdf_files(resume_folder)

    for file in pdf_files:
        text = pdfextract(file)
        matched_skills = extract_skills_from_resume(text, all_skills)
        skill_score = score_against_job(matched_skills, required_skills)
        years_of_exp = extract_years_of_experience(text)
        exp_score = match_experience(years_of_exp, data_dict()["Experience"])
        total_score = skill_score + exp_score
        resume_scores.append((os.path.basename(file), total_score, skill_score, exp_score))

    resume_scores.sort(key=lambda x: x[1], reverse=True)

    for rank, (filename, total_score, skill_score, exp_score) in enumerate(resume_scores, start=1):
        print(f"Rank {rank}: {filename} | Total Score: {total_score} | Skills: {skill_score} | Experience: {exp_score}")

    return resume_scores

def data_dict():
    return {
        "Experience": {
            (0, 2.5): 2,
            (2.5, 5.5): 3,
            (5.5, float('inf')): 5
        }
    }

def find_pdf_files(folder):
    pdf_files = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_files.append(os.path.join(root, file))
    return pdf_files

def save_rankings_to_csv(ranked_resumes, output_path="ranked_resumes.csv"):
    df = pd.DataFrame(ranked_resumes, columns=["Resume", "Total Score", "Skill Score", "Experience Score"])
    df["Rank"] = df["Total Score"].rank(ascending=False, method='min').astype(int)
    df = df.sort_values(by="Total Score", ascending=False)
    df.to_csv(output_path, index=False)

if __name__ == "__main__":
    job_title = input("Enter Job Title: ")
    resume_folder = "./resume_sample"
    job_skills_csv = "job_skills.csv"

    results = rank_resumes_against_job(job_title, resume_folder, job_skills_csv)
    save_rankings_to_csv(results)
