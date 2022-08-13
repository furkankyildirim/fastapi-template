FROM python:3.8.10

ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt . 
RUN pip3 install -r requirements.txt --no-cache-dir

COPY . .
RUN chmod +x runner.sh

ENTRYPOINT ["./runner.sh"]
EXPOSE 8000