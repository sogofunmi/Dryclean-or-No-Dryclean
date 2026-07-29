import boto3
from dotenv import load_dotenv
import os
import pandas as pd
import json
import numpy as np


load_dotenv()

bucket_name = os.getenv("AWS_RAW_DATA")

def extract_from_s3(bucket_name=bucket_name):
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket_name)
    files = response.get("Contents", [])

    if files:
        recent_file = sorted(files, key=lambda x: x["LastModified"])[-1]
        file_key = recent_file["Key"]
        file = s3.get_object(Bucket=bucket_name, Key=file_key)

        raw_file = file["Body"]
        read_file = json.load(raw_file)

        data = pd.DataFrame(read_file)
        data.index = range(1, len(data) + 1)
        
        return data
    else:
        print("No file found in bucket")
    
def care_labels(data):
    wash_labels = set(["hand wash", "machine", "dry clean", "cold washing", "delicate cycle", "gentle cycle", 
               "wash cold", "wash hot", "wash warm", "washable", "specialist clean", "specialist care", "wash at", "spot clean", 
               "professional clean", "delicate wash", "cold wash", "professional textile care", 
               "professional leather cleaning", "specialized care", "leather specialist", "specialist leather"])

    data["y"] = [", ".join([word.lower() for word in row 
                                       for substring in wash_labels 
                                       if substring in word.lower()]) 
                                       for row in data["details"]]

    data.where(data["y"]!="",inplace=True)

    data.dropna(inplace=True)

    condition = data["y"].str.contains("machine wash|cycle|washable at|cold washing|wash at|cold wash", case=False)

    data["y"] = np.where(condition, "1", "0")

    return data["y"]

def price_transform(data): 
    data.dropna(inplace=True)
    data["price"] = data['price'].str.replace(r'[$,]', '', regex=True)
    # have to scale price
    return data["price"]

def composition_transform(data):

    data["composition"] = data["composition"].astype("str")
    data['composition'] = data['composition'].str.replace(r'[\[\]]', '', regex=True)

def transform_data(data):

    data["price"] = price_transform(data)
    links = data["links"]
    data["y"] = care_labels(data)

    data["composition"] = composition_transform(data)

    return links, data

def load_to_s3(links, df):
    s3 = boto3.client("s3")
    s3.put_object(Bucket=bucket_name, Body=links, Key="all_links")

def main():
    links, df = transform_data(extract_from_s3())
    load_to_s3(links, df)

if __name__=="__main__":
    main()
