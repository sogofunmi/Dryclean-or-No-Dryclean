# Dry Clean Prediction Model

## Overview

This repository showcases an end-to-end machine learning deployment pipeline. It features a Flask application containerized with Docker and continuously deployed to AWS via GitLab CI/CD.

## Project Components

1. **Data Ingestion Pipeline**
2. **ETL Pipeline**
3. **Training Pipeline**
4. **Monitoring and Evaluation Pipeline**
5. **Model Serving API**

## How to Run Locally


--default-artifact-root s3://$AWS_TRANSFORMED_DATA/mlflow-artifacts
  scraper:
    build: 
      context: ./fashion_crawler/
    ports:
      - "6800:6800"
    volumes:
      - ~/.aws:/root/.aws

  mlflow_serving:
    build:
      context: ./app


 depends_on:
      - scraper