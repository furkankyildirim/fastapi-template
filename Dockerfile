FROM python:3.8.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# uv'yi kur
RUN pip install uv

# pyproject.toml dosyasını kopyala
COPY pyproject.toml . 

# uv ile bağımlılıkları kur
RUN uv pip install -e .

COPY . .
RUN chmod +x runner.sh

ENTRYPOINT ["./runner.sh"]
EXPOSE 8000