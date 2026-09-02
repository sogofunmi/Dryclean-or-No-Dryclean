FROM python:3.13.15-slim
WORKDIR /farfetch

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y wget gnupg \
    && pip install playwright \
    && playwright install-deps

RUN playwright install chromium

COPY . .

CMD ["scrapy", "crawl", "farfetch"]
EXPOSE 6800