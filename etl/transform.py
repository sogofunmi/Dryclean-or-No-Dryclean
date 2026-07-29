import boto3
from dotenv import load_dotenv
import os
import pandas as pd
import json



load_dotenv()

bucket_name = os.getenv("AWS_RAW_DATA")
prefix = "modaoperandi/raw/"

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
    

def transform_data(data):
    wash_labels = set(["hand wash", "machine", "dry clean", "cold washing", "delicate cycle", "gentle cycle", 
           "wash cold", "wash hot", "wash warm", "washable", "specialist clean", "specialist care", "wash at", "spot clean", 
           "professional clean", "delicate wash", "cold wash", "professional textile care", 
           "professional leather cleaning", "specialized care", "leather specialist", "specialist leather"])

    df = data.dropna()
    df["wash_label"] = [", ".join([word.lower() for word in row 
                                   for substring in wash_labels 
                                   if substring in word.lower()]) 
                                   for row in data["details"]]

def load_to_s3():
    pass

if __name__=="__main__":
    load_to_s3()
