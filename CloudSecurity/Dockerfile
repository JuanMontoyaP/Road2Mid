FROM registry.strln.net/streamline-network-dev/python3-slim-hardened:3.11-slim

WORKDIR /usr/src/code

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

COPY ./app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]