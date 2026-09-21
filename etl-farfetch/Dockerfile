FROM python:3.13.15-slim

WORKDIR /farfetch

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "transform-farfetch.py"] 