FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir 

COPY . .

ENV PORT 8080

# Command to run the application using Gunicorn for production
# Format: CMD exec gunicorn --bind :$PORT [file_name]:[flask_app_variable_name]
CMD exec gunicorn --bind :$PORT --workers 1 main:app