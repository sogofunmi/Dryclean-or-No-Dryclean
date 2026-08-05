FROM python:3.13.14-bookworm

WORKDIR /trainer

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "model_trainer.py"]