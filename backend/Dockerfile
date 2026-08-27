FROM public.ecr.aws/lambda/python:3.13 AS builder

WORKDIR /app

RUN pip install --upgrade pip && \
    pip install cmake \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt --target /app/packages

FROM public.ecr.aws/lambda/python:3.13
WORKDIR ${LAMBDA_TASK_ROOT}

ENV HF_HOME=/tmp/hf_home
ENV TRANSFORMERS_CACHE=/tmp/hf_cache
ENV XDG_CACHE_HOME=/tmp/xdg_cache

COPY --from=builder /app/packages ${LAMBDA_TASK_ROOT}

COPY . .

RUN python -c "from sentence_transformers import SentenceTransformer; \ 
model = SentenceTransformer('all-MiniLM-L6-v2'); \
model.save('${LAMBDA_TASK_ROOT}/models/all-MiniLM-L6-v2/', safe_serialization=True)"


CMD ["main.handler"]