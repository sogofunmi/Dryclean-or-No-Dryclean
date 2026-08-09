# Clothing Care Label Prediction Model

## Overview

This repository showcases an end-to-end machine learning deployment pipeline. It features an automated data ingestion, ETL, and model training pipeline containerized with Docker and continuously deployed to AWS.

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






