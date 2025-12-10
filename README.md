🧠 Intelligent Resume-Based Job Suggestion & Skill-Gap Analysis System
Powered by Openapi AI • RAG • Streamlit • Lambda • MongoDB

This project delivers an AI-driven end-to-end job recommendation system that analyzes resumes, extracts skills using LLMs, retrieves live job listings, performs semantic ranking, identifies missing skills, and presents personalized career recommendations through a Streamlit dashboard.

🚀 Features
✔ Intelligent Resume Upload & Processing
Resume upload via Streamlit
Secure storage in AWS S3 with metadata
Virus scan Lambda validates file integrity
S3 event trigger initiates automated processing pipeline
✔ AI-Powered Resume Understanding
AWS Textract / Comprehend extract structured text
Titan Embeddings generate semantic vector representations
Openai API performs:
Skill summarization
Education extraction
Experience & achievement interpretation
Processed and enriched data stored in MongoDB Atlas with embeddings
✔ RAG-Based Job Retrieval
Fetches job listings from APIs like Adzuna, JSearch, Indeed
Performs semantic vector-based job retrieval
Claude enriches each job with:
Summary
Required skills
Responsibilities
✔ Hybrid Job Ranking Engine
Multi-factor scoring:

final_score = 0.55semantic_similarity + 0.25keyword_overlap + 0.10recency_weight + 0.10popularity_score

✔ Streamlit UI for Real-Time Results
Displays Top 20 job matches
Interactive skill-gap heatmaps
Recommended courses (via Coursera API)
Automated daily refresh (Streamlit → API Gateway → Lambda)
User feedback loop to improve ranking accuracy over time
🏗 System Architecture Overview
Stage 1 — Resume Upload & Pre-Processing
Resume uploaded through Streamlit
File stored in S3 with metadata
Virus scan Lambda validates file and triggers processing
Stage 2 — Resume Parsing & Embedding
Textract/Comprehend extract raw text
Titan embeddings + Claude summarization generate structured profile
Data stored in MongoDB
Stage 3 — RAG Retrieval Layer
Queries job APIs
Job descriptions embedded and indexed
Claude generates summaries + required skills
Stage 4 — Matching & Ranking
Multi-criteria ranking algorithm applied
Missing-skill vector computed
Contextual match explanation generated
Stage 5 — Streamlit Visualization & Continuous Learning
Dashboard shows job matches & analytics
Daily refresh automation
Optional user feedback refinement
📊 Results
Highly context-aware job recommendations (beyond keyword matching)
Automatically generated personalized career summaries
Real-time updating pipeline (S3 → Lambda → Streamlit)
Built-in analytics, including:
Average match score
Industry fit visualization
Most common missing skills
