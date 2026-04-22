FROM python:3.11-slim

WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
    

# copy requirements 1.first this
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# copy project 2.after
COPY . .

EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]