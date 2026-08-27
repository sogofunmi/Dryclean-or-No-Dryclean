FROM python:3.12-slim

RUN pip install --upgrade pip && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install awslambdaric

ENV HF_HOME=/tmp/hf_home
ENV TRANSFORMERS_CACHE=/tmp/hf_cache
ENV XDG_CACHE_HOME=/tmp/xdg_cache

RUN pip install --no-cache-dir -r requirements.txt 

RUN python -c "from sentence_transformers import SentenceTransformer; \ 
    model = SentenceTransformer('all-MiniLM-L6-v2'); \
    model.save('/app/models/all-MiniLM-L6-v2/', safe_serialization=True)" 

COPY . .

ENTRYPOINT ["/usr/local/bin/python", "-m", "awslambdaric"]

CMD ["main.handler"]