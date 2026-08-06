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

  rules:
    - if: $CI_COMMIT_BRANCH == "master"
      changes:
        - fashion_crawler/**/*

