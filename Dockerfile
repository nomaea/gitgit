FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y netcat-openbsd

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

COPY wait-for-it.sh /wait-for-it.sh
RUN chmod +x /wait-for-it.sh