FROM python:3.11-slim

WORKDIR /app

# Install SQLite and development tools
RUN apt-get update && \
    apt-get install -y sqlite3 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory with proper permissions
RUN mkdir -p /home/site/wwwroot/data && \
    chmod 777 /home/site/wwwroot/data

COPY . .

ENV FLASK_APP=app
ENV FLASK_ENV=production
ENV HOME=/home/site/wwwroot

EXPOSE 5000

# Run deployment script and then start Flask app
CMD python deploy.py && flask run --host=0.0.0.0 