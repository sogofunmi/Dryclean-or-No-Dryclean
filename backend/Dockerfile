FROM python:3.12-slim

RUN pip install --upgrade pip && \
    pip install cmake && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install awslambdaric

RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

ENTRYPOINT ["/usr/local/bin/python", "-m", "awslambdaric"]

CMD ["main.handler"]