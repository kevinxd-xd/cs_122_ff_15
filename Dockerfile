# Taken from "Deploy Flask App to the Cloud" lecture

FROM python:3.12.1

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

VOLUME /app/data

EXPOSE 5000

CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]