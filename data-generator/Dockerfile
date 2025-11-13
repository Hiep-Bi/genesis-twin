FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -u 1000 genesis && chown -R genesis:genesis /app
USER genesis

CMD ["python", "generate_data.py"]

