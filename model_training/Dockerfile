FROM python:3.13.14-bookworm

WORKDIR /trainer

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


RUN python -c "from sentence_transformers import SentenceTransformer; \ 
model = SentenceTransformer('all-MiniLM-L6-v2'); \
model.save('/trainer/models/all-MiniLM-L6-v2')"

COPY . .

ENV MODEL_PATH=/trainer/models/all-MiniLM-L6-v2

CMD ["python", "model_trainer.py"]