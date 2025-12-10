# lambda_function.py
import os
import json
import tempfile
import boto3
import fitz  # PyMuPDF for PDF text extraction
import docx
import pymongo
from datetime import datetime
import requests
import re
from difflib import SequenceMatcher
from dateutil.parser import parse as parse_date
from openai import OpenAI

# ----------------------------
# Configuration (from env vars)
# ----------------------------
# ⚠ Set these in Lambda console: Configuration -> Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MONGO_URI = os.getenv("MONGO_URI", "")  # 
BUCKET = os.getenv("RESUME_BUCKET", "")
FOLDER_PREFIX = os.getenv("RESUME_PREFIX", "")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")

# ------------------------------------------------
# Initialize clients (reuse across invocations)
# ------------------------------------------------
s3_client = boto3.client("s3")
_mongo_client = None

def get_mongo_client():
    """Lazily create and cache the MongoDB client."""
    global _mongo_client
    if _mongo_client is None:
        if not MONGO_URI:
            raise RuntimeError("MONGO_URI is not set")
        _mongo_client = pymongo.MongoClient(MONGO_URI)
    return _mongo_client

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set")

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# -----------------------------
# 1) Fetch latest resume from S3
# -----------------------------
def fetch_latest_resume_from_s3(bucket=BUCKET, prefix=FOLDER_PREFIX):
    resp = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix)
    if "Contents" not in resp or len(resp["Contents"]) == 0:
        raise RuntimeError("No resumes found in S3 folder.")
    # Sort by LastModified desc and pick the latest
    latest = sorted(resp["Contents"], key=lambda x: x["LastModified"], reverse=True)[0]
    key = latest["Key"]
    filename = os.path.basename(key)
    _, ext = os.path.splitext(filename)

    tmp = tempfile.NamedTemporaryFile(prefix="resume_", suffix=ext, delete=False)
    tmp.close()
    local_path = tmp.name

    s3_client.download_file(bucket, key, local_path)
    return local_path, filename, key, latest["LastModified"]

# -----------------------------
# 2) Extract text from resume
# -----------------------------
def extract_text_from_file(path: str) -> str:
    text = ""
    lower = path.lower()

    if lower.endswith(".pdf"):
        # Use PyMuPDF (fitz) for PDFs
        with fitz.open(path) as pdf:
            for page in pdf:
                # "text" for plain text; use "blocks" or "dict" if you need more structure
                t = page.get_text("text")
                if t:
                    text += t + "\n"

    elif lower.endswith(".docx"):
        doc = docx.Document(path)
        for para in doc.paragraphs:
            text += para.text + "\n"

    else:
        # fallback: try reading as plain text
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    return text

# -----------------------------
# OpenAI helper (extract JSON safely)
# -----------------------------
def _extract_json_from_text(resp_text: str) -> dict:
    m = re.search(r"\{.*\}", resp_text, re.DOTALL)
    if not m:
        return {}
    try:
        return json.loads(m.group())
    except Exception:
        return {}

def summarize_resume_sections(resume_text: str) -> dict:
    prompt = f"""
You are an AI resume summarizer.
Extract and summarize the following sections:
- Education
- Skills
- Roles
- Achievements

Return JSON exactly in this format:
{{"education": [...], "skills": [...], "roles": [...], "achievements": [...]}}

Resume:
{resume_text}
"""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.25,
            max_tokens=800,
        )
        return _extract_json_from_text(resp.choices[0].message.content.strip())
    except Exception as e:
        print("OpenAI summarize error:", e)
        return {}

def extract_resume_skills(resume_text: str) -> dict:
    prompt = f"""
You are an AI recruiter. Return JSON exactly:
{{"roles": [...], "skills": [...], "industries": [...]}}

Resume:
{resume_text}
"""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        return _extract_json_from_text(resp.choices[0].message.content.strip())
    except Exception as e:
        print("OpenAI extract skills error:", e)
        return {}

def generate_embeddings(resume_text: str):
    try:
        resp = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=resume_text,
        )
        return resp.data[0].embedding
    except Exception as e:
        print("OpenAI embedding error:", e)
        return []

# -----------------------------
# Jobs via Adzuna
# -----------------------------
def fetch_jobs_for_resume(resume_summary: dict, country: str = "in", pages: int = 1, per_page: int = 20) -> list:
    queries = resume_summary.get("roles", []) + resume_summary.get("skills", [])
    all_jobs = []

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("Adzuna credentials not configured; skipping job fetch.")
        return []

    for query in queries:
        for page in range(1, pages + 1):
            url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_APP_KEY,
                "results_per_page": per_page,
                "what": query,
            }
            try:
                r = requests.get(url, params=params, timeout=15)
                if r.status_code == 200:
                    all_jobs.extend(r.json().get("results", []))
                else:
                    print(f"Adzuna error status {r.status_code} for query {query}")
            except Exception as e:
                print("Adzuna request error:", e)

    # De-duplicate by job["id"]
    unique = {job["id"]: job for job in all_jobs if "id" in job}.values()
    return list(unique)

def enrich_job(description: str, candidate_roles: list, candidate_skills: list) -> dict:
    prompt = f"""
You are an AI recruiter. Given candidate roles: {candidate_roles} and skills: {candidate_skills},
analyze the job description and return JSON:
{{"summary": "...", "skills": [...], "responsibilities": [...]}}

Job Description:
{description}
"""
    try:
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300,
        )
        return _extract_json_from_text(resp.choices[0].message.content.strip())
    except Exception as e:
        print("OpenAI enrich job error:", e)
        return {}

# -----------------------------
# Store resume and jobs in MongoDB
# -----------------------------
def store_resume_to_db(file_name: str, s3_key: str, text: str, last_modified) -> dict:
    db = get_mongo_client().job_db
    summary = summarize_resume_sections(text)
    extracted = extract_resume_skills(text)
    embedding = generate_embeddings(text)

    doc = {
        "resume_id": os.path.splitext(file_name)[0],
        "s3_key": s3_key,
        "file_name": file_name,
        "resume_text": text,
        "summary": summary,
        "extracted": extracted,
        "embedding": embedding,
        "metadata": {
            "source_bucket": BUCKET,
            "upload_time": last_modified.isoformat() if hasattr(last_modified, "isoformat") else str(last_modified),
            "processed_at": datetime.utcnow().isoformat(),
            "file_type": os.path.splitext(file_name)[1],
        },
    }

    result = db.resumes.insert_one(doc)
    doc["_id"] = result.inserted_id
    return doc

def store_jobs_to_db(enriched_jobs: list):
    db = get_mongo_client().job_db
    if enriched_jobs:
        db.jobs.insert_many(enriched_jobs)

# -----------------------------
# Hybrid matching & ranking
# -----------------------------
def hybrid_match_rank(resume_text: str, candidate_skills: list, jobs: list, top_k: int = 10):
    matches = []
    candidate_skill_set = set(candidate_skills)

    for job in jobs:
        sem_sim = SequenceMatcher(
            None,
            resume_text.lower(),
            (job.get("summary") or "").lower(),
        ).ratio()

        job_skills = set(job.get("skills") or [])
        keyword_overlap = (
            len(candidate_skill_set & job_skills) / len(job_skills) if job_skills else 0
        )

        posting_date = job.get("posting_date")
        if posting_date:
            try:
                days_old = (datetime.utcnow() - parse_date(posting_date)).days
                recency_weight = max(0, 1 - days_old / 90)
            except Exception:
                recency_weight = 0.5
        else:
            recency_weight = 0.5

        popularity_score = min(job.get("popularity_score", 0) / 100000, 1)

        final_score = (
            0.55 * sem_sim
            + 0.25 * keyword_overlap
            + 0.10 * recency_weight
            + 0.10 * popularity_score
        )

        missing_skills = list(job_skills - candidate_skill_set)

        explanation_text = "No explanation generated."
        try:
            resp = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "user",
                        "content": f"Explain match for skills {list(candidate_skill_set)} vs {list(job_skills)} in 2 sentences.",
                    }
                ],
                temperature=0.4,
                max_tokens=120,
            )
            explanation_text = resp.choices[0].message.content.strip()
        except Exception as e:
            print("OpenAI explanation error:", e)

        match_doc = {
            "job_id": job.get("job_id") or job.get("id"),
            "title": job.get("title"),
            "company": job.get("company"),
            "final_score": round(final_score, 3),
            "semantic_similarity": round(sem_sim, 3),
            "keyword_overlap": round(keyword_overlap, 3),
            "recency_weight": round(recency_weight, 3),
            "popularity_score": round(popularity_score, 3),
            "missing_skills": missing_skills,
            "contextual_explanation": explanation_text,
            "matched_at": datetime.utcnow().isoformat(),
        }
        matches.append(match_doc)

    matches.sort(key=lambda x: x["final_score"], reverse=True)
    top_matches = matches[:top_k]

    db = get_mongo_client().job_db
    if top_matches:
        db.matches.insert_many(top_matches)
        s3_key = f"matches/matches_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.json"
        s3_client.put_object(
            Bucket=BUCKET,
            Key=s3_key,
            Body=json.dumps(top_matches, default=str).encode("utf-8"),
        )
        return top_matches, s3_key

    return [], None

# -----------------------------
# Lambda handler
# -----------------------------
def lambda_handler(event, context):
    try:
        # If event is an S3 create event, use the object passed in the event
        if event and isinstance(event, dict) and "Records" in event and event["Records"]:
            rec = event["Records"][0]
            s3_info = rec.get("s3", {})
            bucket_name = s3_info.get("bucket", {}).get("name", BUCKET)
            key = s3_info.get("object", {}).get("key")
            if not key:
                raise RuntimeError("S3 event missing object key")

            _, ext = os.path.splitext(key)
            tmp = tempfile.NamedTemporaryFile(prefix="resume_", suffix=ext, delete=False)
            tmp.close()
            s3_client.download_file(bucket_name, key, tmp.name)
            local_path, file_name, s3_key, last_modified = (
                tmp.name,
                os.path.basename(key),
                key,
                datetime.utcnow(),
            )
        else:
            local_path, file_name, s3_key, last_modified = fetch_latest_resume_from_s3()

        text = extract_text_from_file(local_path)
        stored_doc = store_resume_to_db(file_name, s3_key, text, last_modified)
        extracted = stored_doc.get("extracted", {})
        candidate_roles = extracted.get("roles", [])
        candidate_skills = extracted.get("skills", [])

        jobs = fetch_jobs_for_resume(extracted, pages=1, per_page=10)
        enriched_docs = []

        if jobs:
            for job in jobs:
                enriched_info = enrich_job(
                    job.get("description", ""),
                    candidate_roles,
                    candidate_skills,
                )
                job_doc = {
                    "job_id": job.get("id"),
                    "title": job.get("title"),
                    "company": job.get("company", {}).get("display_name"),
                    "summary": enriched_info.get("summary"),
                    "skills": enriched_info.get("skills"),
                    "responsibilities": enriched_info.get("responsibilities"),
                    "posting_date": job.get("created"),
                    "source": "adzuna",
                    "created_at": datetime.utcnow().isoformat(),
                }
                enriched_docs.append(job_doc)

            if enriched_docs:
                store_jobs_to_db(enriched_docs)

        matches, s3_matches_key = hybrid_match_rank(
            text, candidate_skills, enriched_docs, top_k=10
        )

        result = {
            "status": "ok",
            "file_name": file_name,
            "stored_doc_id": str(stored_doc.get("_id")),
            "num_jobs_enriched": len(enriched_docs),
            "num_matches": len(matches),
            "matches_s3_key": s3_matches_key,
        }
        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception as e:
        print("Pipeline error:", e)
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
