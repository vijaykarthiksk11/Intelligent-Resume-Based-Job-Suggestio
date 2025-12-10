# Python 3.11 base image எடுத்துக்கலாம்
FROM python:3.11

# வேலை செய்ய ஒரு working directory உருவாக்கலாம்
WORKDIR /app

# requirements.txt ஐ copy பண்ணும்
COPY requirements.txt .

# dependencies install பண்ணலாம் (அதே /app folderக்குள்)
RUN pip install --no-cache-dir -r requirements.txt -t .

# உங்க lambda_function.py & மற்ற source files இங்க copy பண்ணும்
# (if everything is in same folder as Dockerfile, this copies all)
COPY . .

# finalா deployment.zip பண்ணிடலாம் - /app மட்டும் zip பண்ணும்
RUN apt-get update && apt-get install -y zip && \
    cd /app && zip -r /app/deployment.zip .