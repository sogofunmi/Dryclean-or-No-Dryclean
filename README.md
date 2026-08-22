# Clothing Care Label Prediction Model

## Overview

This repository showcases an end-to-end machine learning deployment pipeline. It features an automated data ingestion, ETL, and model training pipeline containerized with Docker and continuously deployed to AWS.

## 🛠️ Tech Stack

|Category | Technology | Purpose |
| --- | --- | --- |
| Application | React, FastAPI | Full stack ML prediction web application |
| CI/CD | GitLab CI | Deployment |
| Compute | Fargate | Application hosting, auto scraping and processing, continuous training |
| Containerization | Docker, Docker Compose | Container runtime and orchestration |
| Container Registry | Amazon ECR | Private docker image storage |
| Experiment Tracking | MLflow | Tracks all experiments and logs production model and artifacts |
| Hyperparameter Tuning | Optuna | Tunes hyperparams to maximize F1 score |
| Infrastructure | Terraform | Infrastructure as Code |
| Model | XGBoost | Prediction model |
| Reverse Proxy | Nginx | Traffic Routing |
| Data Storage | AWS S3, Postgres | Stores scraped data, transformed data, and mlflow artifacts |
| SSL | AWS ACM | HTTPS Certificate |


## 📁 Project Structure

```text
├── backend
│   ├── inference.py
│   └── requirements.txt
├── etl
│   ├── Dockerfile
│   ├── __init__.py
│   ├── requirements.txt
│   └── transform.py                       
├── fashion_crawler
│   ├── Dockerfile
│   ├── fashion_crawler                     
│   │   ├── __init__.py
│   │   ├── items.py
│   │   ├── middlewares.py
│   │   ├── pipelines.py
│   │   ├── settings.py
│   │   └── spiders
│   │       ├── __init__.py
│   │       └── fashion_spider.py
│   ├── requirements.txt
│   └── scrapy.cfg
├── mlflow
│   └── Dockerfile
├── model_training
│   ├── Dockerfile
│   ├── __init__.py
│   ├── model_trainer.py
│   └── requirements.txt
├── notebooks
├── README.md
├── .gitlab-ci.yml
├── docker-compose.yml
├── .gitignore
└── requirements.txt
```

## Project Components

1. **Data Ingestion:** Automated to handle large scale scraping from the Moda Operandi website. Scraping, ETL, and training runs on a monthly schedule using Amazon EventBridge and step functions. 
2. **ETL Pipeline:** Designed to handle data extraction and cleaning.  
3. **Model Training and Evaluation:** Designed for iterative experimentation and training, focusing on an XGBoost model with Optuna for hyperparameter tuning and MLflow for experiment tracking, to identify the most effective prediction method.






