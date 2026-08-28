# Clothing Care Label Prediction Model

## Full Stack ML Web App

![Static Badge](https://img.shields.io/badge/Python-orange?style=flat&logo=python&logoColor=blue) ![Static Badge](https://img.shields.io/badge/AWS-purple?style=flat&logoColor=blue) ![Static Badge](https://img.shields.io/badge/GitLab%20CI-purple?style=flat&logo=gitlab&logoColor=blue) ![Static Badge](https://img.shields.io/badge/Docker-purple?style=flat&logo=docker&logoColor=blue) ![Static Badge](https://img.shields.io/badge/MLflow-orange?style=flat&logo=mlflow&logoColor=blue)  ![Static Badge](https://img.shields.io/badge/Terraform-orange%3Fstyle%3Dflat%26logo%3Dgrafana%26logoColor%3Dblue?style=flat&logo=terraform&logoColor=blue&color=orange) ![Static Badge](https://img.shields.io/badge/FastAPI-purple?style=flat&logo=fastapi&logoColor=blue) ![Static Badge](https://img.shields.io/badge/ReactJS-orange?style=flat&logo=react&logoColor=blue)

This repository showcases a full stack ML web app. It features automated data ingestion, ETL, and model training pipelines containerized with Docker and deployed to AWS using GitLab and Terraform.

## Project Components

1. **Data Ingestion Pipeine:** Automated to handle large scale scraping from the Moda Operandi website. Scraping, ETL, and training runs on a monthly schedule using Amazon EventBridge rules and schedules.
2. **ETL Pipeline:** Designed to handle data extraction and cleaning. This pipeline focuses on specifically extracting the fabric care components from fabic description strings. Fiber names were extracted from the composition column using regex to find fiber names based on custim dictionaries for clothing fiber abbreviations and fiber substitutions.
3. **Model Training and Evaluation:** Designed for iterative experimentation and training, focusing on an XGBoost model with Optuna for hyperparameter tuning and MLflow for experiment tracking. Scaler used and 
4. **Model Serving API:** FastAPI, Lambda, and API Gateway (REST API) work well together for the backend. Lambda + API Gateway are cost effective when running a low traffic site  because of their serverless offering. API Gateway provides rate limiting, throttling, and other protections for the backend
5. **Frontend:** S3 + CloudFront were used for the frontend. S3 is great for hosting static websites and CloudFront provides some protecton with the Web ACL.
6. **Infrastructure Provisioning:** Terraform was used for provisioning infrastructure specifically for the CloudFront distribution and Lambda + API Gateway infrastructure (backend). 
6. **Full Model Deployment**: Model was deployed to AWS using GitLab CI. Continuous retraining and deployment are automated using AWS Services like lambda functions and EventBridge rules.

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


