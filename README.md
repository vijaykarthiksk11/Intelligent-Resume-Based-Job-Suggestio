#Intelligent Resume-Based Job Suggestion & Skill-Gap Analysis System
Using AWS Bedrock, RAG Architecture, and Streamlit
#🚀 Overview

Traditional job portals rely on keyword matching and fail to understand the deeper context of a candidate’s skills.
This project builds an AI-powered job recommendation system that analyzes resumes, retrieves live job data, detects skill gaps, and provides personalized career recommendations using:

AWS Bedrock (Claude 3.5, Titan Embeddings)

RAG (Retrieval-Augmented Generation) architecture

AWS Lambda + S3 + API Gateway

MongoDB Atlas vector search

Streamlit Dashboard

The system generates contextual job matches, skill-gap insights, and recommended learning paths.

#🧠 Key Features
1. Intelligent Resume Parsing

Upload resume (PDF/DOCX) via Streamlit.

Stored in S3 → processed automatically via Lambda.

AWS Textract & Comprehend extract structured text.

Claude summarizes roles, skills, achievements.

2. Embedding & RAG Layer

Titan Embeddings generate semantic vectors for resumes & jobs.

RAG retrieves top-k relevant job documents from job APIs + vector DB.

3. Hybrid Job Ranking Engine

A multi-weight scoring formula:

final_score =
0.55 * semantic_similarity +
0.25 * keyword_overlap +
0.10 * recency_weight +
0.10 * popularity_score


Detects missing skills.

Generates “Why this job matches you”.

4. Streamlit Dashboard

Top 20 job recommendations.

Skill-gap heatmap.

Recommended courses (Coursera API).

Daily refresh → triggers Lambda.

5. Continuous Learning

User feedback (like/dislike) adjusts ranking weights over time.

#🏗️ System Architecture
Streamlit → S3 → Lambda → Textract/Bedrock → MongoDB (Vector DB)
                    ↓
             Job APIs (Adzuna/JSearch)
                    ↓
               Ranking Engine
                    ↓
              Streamlit Dashboard


All modules are event-driven and follow a serverless pipeline.
#📂 Datasets / Data Sources
1. Resume Dataset

Source: User upload

Format: PDF / DOCX

Stored in: S3 → processed via Textract

Fields Extracted:

Name, email, phone

Education

Skills (technical/non-technical)

Work experience

Achievements

2. Job Dataset (Live Job APIs)

Sources:

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

3. Internal Skill Corpus

Generated using Claude on Bedrock

Used for:

Skill normalization

Mapping skills → categories

Skill gap detection
⚙️ Workflow Summary
Stage 1 — Resume Upload

Streamlit → S3 → Lambda trigger

Stage 2 — Parsing & Embeddings

Textract → Claude → Titan Embeddings → MongoDB

Stage 3 — Job Retrieval

API calls → Normalize → Vector search → Store

Stage 4 — Ranking

Semantic matching

Skill gap analysis

Weighted scoring

Stage 5 — Dashboard

Interactive visualization

Job match insights

Skill heatmap

Course recommendations
#🌐 Business Use Cases

Automated resume screening (HR)

Career counseling platforms

E-learning + course recommendations

Internal job mobility for enterprises

AI career assistant bots
