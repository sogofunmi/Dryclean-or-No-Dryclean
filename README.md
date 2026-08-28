# Clothing Care Label Prediction Model

## Full Stack ML Web App

![Static Badge](https://img.shields.io/badge/Python-orange?style=flat&logo=python&logoColor=blue) ![Static Badge](https://img.shields.io/badge/AWS-purple?style=flat&logoColor=blue) ![Static Badge](https://img.shields.io/badge/GitLab%20CI-purple?style=flat&logo=gitlab&logoColor=blue) ![Static Badge](https://img.shields.io/badge/Docker-purple?style=flat&logo=docker&logoColor=blue) ![Static Badge](https://img.shields.io/badge/MLflow-orange?style=flat&logo=mlflow&logoColor=blue)  ![Static Badge](https://img.shields.io/badge/Terraform-orange%3Fstyle%3Dflat%26logo%3Dgrafana%26logoColor%3Dblue?style=flat&logo=terraform&logoColor=blue&color=orange) 

## Overview

This repository showcases an end-to-end machine learning deployment pipeline. It features an automated data ingestion, ETL, and model training pipeline containerized with Docker and continuously deployed to AWS.


## Project Structure

```text
├── backend
│   ├── Dockerfile
│   ├── inference.py
│   ├── main.py
│   └── requirements.txt
├── etl
│   ├── Dockerfile
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
├── frontend
│   ├── Dockerfile
│   ├── nginx.conf
│   └── (React source)
├── mlflow
│   └── Dockerfile
├── model_training
│   ├── Dockerfile
│   ├── model_trainer.py
│   └── requirements.txt
├── notebooks
├── terraform
│   ├── backend.tf
│   ├── main.tf
│   ├── variables.tf
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


## Local Development

```text
git clone https://github.com/sogofunmi/Dryclean-or-No-Dryclean.git
cd Dryclean-or-No-Dryclean

# Copy environment template and fill in local values in .env
cp .env.example .env

#Start all services locally and view logs 
docker compose up -d
docker compose logs -f

# Stop all services
docker compose down
```

