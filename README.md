Intelligent Resume-Based Job Suggestion & Skill-Gap Analysis System Using AWS Bedrock, RAG Architecture, and Streamlit
🚀 Overview

Traditional job portals rely on keyword matching and fail to understand the deeper context of a candidate’s skills.
This project builds an AI-powered job recommendation system that:

Analyzes resumes

Retrieves live job data

Detects skill gaps

Provides personalized career recommendations

Using:

AWS Bedrock (Claude 3.5, Titan Embeddings)

RAG (Retrieval-Augmented Generation)

AWS Lambda + S3 + API Gateway

MongoDB Atlas Vector Search

Streamlit Dashboard

🧠 Key Features
Intelligent Resume Parsing

Upload resume (PDF/DOCX) via Streamlit

Stored in S3 → processed via Lambda

AWS Textract & Comprehend extract text

Claude summarizes roles, skills, achievements

Embedding & RAG Layer

Titan Embeddings generate semantic vectors

RAG retrieves top-k relevant job documents

Hybrid Job Ranking Engine
final_score =
0.55 * semantic_similarity +
0.25 * keyword_overlap +
0.10 * recency_weight +
0.10 * popularity_score


Detects missing skills

Generates “Why this job matches you”

Streamlit Dashboard

Top 20 job recommendations

Skill-gap heatmap

Recommended courses (Coursera API)

Daily refresh → triggers Lambda

Continuous Learning

User feedback (like/dislike) updates ranking weights

🏗️ System Architecture
Streamlit → S3 → Lambda → Textract/Bedrock → MongoDB (Vector DB)
                    ↓
             Job APIs (Adzuna/JSearch)
                    ↓
               Ranking Engine
                    ↓
            Streamlit Dashboard


All modules are event-driven and follow a serverless pipeline.

📂 Datasets / Data Sources
Resume Dataset

Source: User upload

Format: PDF / DOCX

Stored in S3 → processed via Textract

Extracted Fields:

Name, email, phone

Education

Skills

Work experience

Achievements

Job Dataset (Live APIs)

Adzuna API

JSearch API

Indeed Open API

Fields:

Job title

Company

Description

Skills required

Salary

Location

Vector embeddings

Internal Skill Corpus

Generated using Claude on Bedrock
Used for:

Skill normalization

Skills → category mapping

Skill-gap detection

⚙️ Workflow Summary
Stage 1 — Resume Upload

Streamlit → S3 → Lambda trigger

Stage 2 — Parsing & Embeddings

Textract → Claude → Titan Embeddings → MongoDB

Stage 3 — Job Retrieval

API calls → Normalize → Vector search → Store

Stage 4 — Ranking

Semantic matching

Skill-gap analysis

Weighted scoring

Stage 5 — Dashboard

Interactive visualization

Job match insights

Skill heatmap

Course recommendations

🌐 Business Use Cases

Automated resume screening (HR)

Career counseling platforms

E-learning + course recommendations

Internal job mobility for enterprises

AI career assistant bots

If you want, I can also format the entire README with tables, icons, badges, and TOC (Table of Contents).
