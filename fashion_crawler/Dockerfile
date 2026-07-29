FROM python:3.13.14-bookworm
WORKDIR /data_ingestion/fashion_crawler

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y wget gnupg \
    && pip install playwright \
    && playwright install-deps

RUN playwright install chromium

COPY . .

ENV PYTHONPATH="/"

CMD ["scrapy", "crawl", "fashion"]
EXPOSE 6800