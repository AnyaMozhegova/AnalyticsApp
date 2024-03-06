FROM python:3.10-slim-bullseye

RUN apt-get update && \
  apt-get install -y python3-setuptools && \
  apt-get purge -y python3-pip && \
  rm -rf /var/cache/apt

WORKDIR /app

RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3.10
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
