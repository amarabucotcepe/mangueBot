FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y sqlite3 libsqlite3-dev

COPY . .


CMD ["streamlit", "run", "mangue.py", "--server.address", "0.0.0.0"]