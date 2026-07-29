FROM python:3.13.14-bookworm

WORKDIR /etl

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "transform.py"] 