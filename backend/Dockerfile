FROM public.ecr.aws/lambda/python:3.13 

RUN pip install --upgrade pip && \
    pip install cmake \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ${LAMBDA_TASK_ROOT}

RUN pip install --no-cache-dir --upgrade pip wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt 

RUN python -c "from sentence_transformers import SentenceTransformer; \ 
    model = SentenceTransformer('all-MiniLM-L6-v2'); \
    model.save('${LAMBDA_TASK_ROOT}/models/all-MiniLM-L6-v2/', safe_serialization=True)"

ENV HF_HOME=/tmp/hf_home
ENV TRANSFORMERS_CACHE=/tmp/hf_cache
ENV XDG_CACHE_HOME=/tmp/xdg_cache

COPY . ${LAMBDA_TASK_ROOT}

CMD ["main.handler"]