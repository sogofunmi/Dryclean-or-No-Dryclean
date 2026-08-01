import os
import pandas as pd


historical_bucket = os.environ.get("AWS_TRANSFORMED_DATA")

def train():
    data = pd.read_csv(f"s3://{historical_bucket}/historical_data.csv")

def pca():
    pass

def embedding():
    pass

def main():
    pass

if __name__ == "__main__":
    main()