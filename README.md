#Intelligent Resume-Based Job Suggestion & Skill-Gap Analysis System Using AWS Bedrock, RAG Architecture, and Streamlit
##🚀 Overview

Traditional job portals rely on simple keyword matching and fail to understand the deeper context of a candidate’s skills.
This project builds an AI-powered job recommendation system that:

Analyzes resumes

Retrieves live job data

Detects missing skills

Provides personalized job recommendations

Suggests courses to fill skill gaps

Powered By:

AWS Bedrock (Claude 3.5 Sonnet, Titan Embeddings)

RAG (Retrieval-Augmented Generation)

AWS Lambda + S3 + API Gateway

MongoDB Atlas Vector Search

Streamlit Dashboard

##🧠 Key Features
1. Intelligent Resume Parsing

Upload resume (PDF/DOCX) via Streamlit

Stored in S3 → Automatically processed through Lambda

AWS Textract extracts text

Claude summarizes:

Roles

Skills

Projects

Achievements

2. Embedding & RAG Layer

Titan Embeddings generate semantic vectors

Vector search retrieves the most relevant jobs from API data

RAG provides contextual reasoning

3. Hybrid Job Ranking Engine
final_score =
0.55 * semantic_similarity +
0.25 * keyword_overlap +
0.10 * recency_weight +
0.10 * popularity_score


Detects missing skills

Generates “Why this job matches your profile”

4. Streamlit Dashboard

Displays Top 20 job matches

Skill-gap heatmap

Recommended courses (Coursera API)

“Daily refresh” to auto-fetch new jobs

5. Continuous Learning

User like/dislike feedback

Re-adjusts ranking weights over time

##🏗️ System Architecture
Streamlit → S3 → Lambda → Textract/Bedrock → MongoDB (Vector DB)
                    ↓
             Job APIs (Adzuna/JSearch)
                    ↓
               Ranking Engine
                    ↓
            Streamlit Dashboard


All components follow a serverless and event-driven design.

##📂 Datasets / Data Sources
1. Resume Dataset

Source: User upload

Format: PDF, DOCX

Stored: AWS S3

Extracted Fields:

Personal info

Skills

Experience

Education

Achievements

2. Job Dataset (Live APIs)

APIs Used:

Adzuna

JSearch

Indeed Open API

Fields Extracted:

Job title

Description

Company

Required skills

Salary

Location

Vector embeddings

3. Internal Skill Corpus

Generated via Claude on Bedrock
Used for:

Skill normalization

Categorization

Skill-gap detection

##⚙️ Workflow Summary
Stage 1 — Resume Upload

Streamlit → S3 → Lambda Trigger

Stage 2 — Parsing & Embeddings

Textract → Claude → Titan Embeddings → MongoDB

Stage 3 — Job Retrieval

API Calls → Normalization → Vector Search → Store in DB

Stage 4 — Ranking

Semantic similarity

Keyword overlap

Recency

Popularity

Skill-gap analysis

Stage 5 — Dashboard

Job matches

Skill heatmap

Gap analysis

Course recommendation

##🌐 Business Use Cases

Automated hiring and resume screening

Career counseling platforms

E-learning platforms with course recommendations

Internal job mobility in enterprises

AI career assistant bots
