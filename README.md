# Clothing Care Label Prediction Model

## Full Stack ML Web App

![Static Badge](https://img.shields.io/badge/Python-orange?style=flat&logo=python&logoColor=blue) ![Static Badge](https://img.shields.io/badge/AWS-purple?style=flat&logoColor=blue) ![Static Badge](https://img.shields.io/badge/GitLab%20CI-purple?style=flat&logo=gitlab&logoColor=blue) ![Static Badge](https://img.shields.io/badge/Docker-purple?style=flat&logo=docker&logoColor=blue) ![Static Badge](https://img.shields.io/badge/MLflow-orange?style=flat&logo=mlflow&logoColor=blue)  ![Static Badge](https://img.shields.io/badge/Terraform-orange%3Fstyle%3Dflat%26logo%3Dgrafana%26logoColor%3Dblue?style=flat&logo=terraform&logoColor=blue&color=orange) ![Static Badge](https://img.shields.io/badge/FastAPI-purple?style=flat&logo=fastapi&logoColor=blue) ![Static Badge](https://img.shields.io/badge/ReactJS-orange?style=flat&logo=react&logoColor=blue)

This repository showcases a full stack ML web app. It features automated data ingestion, ETL, and model training pipelines containerized with Docker and deployed to AWS using GitLab and Terraform.

## Project Components

1. **Data Ingestion Pipeine:** Automated to handle large scale scraping from the Moda Operandi website. All scraped data is stored in an S3 bucket, triggering the ETL pipeline when a new file is added. Scraping runs on a regular schedule automated by EventBridge.
2. **ETL Pipeline:** Designed to handle data extraction and cleaning. Highly imbalanced dataset (89-11) with a positively skewed price column. RobustScaler was used due to its sensitivity to outliers and skewed distributions. Fabric names and percentages were extracted from the composition column using regex based on custom dictionaries for clothing fabric abbreviations and fabric substitutions. Centered Log-Ratio transformation was applied on fabric percentages due to their compositional nature ensuring all data is accurately captured. Title embeddings were obtained using the all-MiniLM-L6-v2 transformer from the HuggingFace sentence-transformers library. Care components e.g. machine wash, hand wash, dry clean, specialist clean etc, were extracted and labelled either 1 for machine washable or 0 for not machine washable.
3. **Model Training and Evaluation:** Designed for iterative experimentation and training, focusing on an XGBoost model with Optuna for hyperparameter tuning and MLflow for experiment tracking. Each model is registered in MLflow and a "production" alias is assigned to the best performing model. The HuggingFace model is also registered into MLflow and is loaded during inference to prevent API Gateway timeouts due to the 30 second limit. Model artifacts like the scaler and DictVectorizer are logged into MLflow as well and loaded during inference for processing. 
4. **Model Serving API:** FastAPI, Lambda, and API Gateway (REST API) work well together for the backend. Lambda + API Gateway are cost effective when running a low traffic site because of their serverless offering. API Gateway provides rate limiting, throttling, and other protections for the backend.
5. **Frontend:** S3 + CloudFront were used for the frontend. S3 is great for hosting static websites and CloudFront provides some protecton with Web ACL. Rate limiting rules were set to block IP addresses with too many requests. 
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


