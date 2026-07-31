import boto3
import os
import pandas as pd
import json
import numpy as np
import re
from sklearn.feature_extraction import DictVectorizer


raw_bucket = os.environ.get("AWS_RAW_DATA")
historical_bucket = os.environ.get("AWS_TRANSFORMED_DATA")

wash_labels = set(["hand wash", "machine", "dry clean", "cold washing", "delicate cycle", "gentle cycle", 
               "wash cold", "wash hot", "wash warm", "washable", "specialist clean", "specialist care", "wash at", "spot clean", 
               "professional clean", "delicate wash", "cold wash", "professional textile care", 
               "professional leather cleaning", "specialized care", "leather specialist", "specialist leather"])

fiber_abb = {"ac": "acetate", "ca":"acetate", "cmd": "modal", "co": "cotton", "cta": "acetate",
            "cu": "cupro", "cup": "cupro", "cv": "viscose", "ea": "elastane", "el": "elastane",
            "hl": "linen", "li": "linen", "ma": "acrylic", "mo": "modal", "me": "metallic", "ny": "polyamide",
            "pe": "polyester", "pes": "polyester", "pet": "polyester", "pm": "polyester", "pu": "polyester",
            "ra": "ramie", "se": "silk", "ta": "acetate", "vi": "viscose", "wa": "wool", "wg": "wool", "wk": "wool",
            "wl": "wool", "wm": "wool", "wp": "wool", "ws": "wool", "wy": "wool", "wv": "wool", "wo": "wool",
            "wu": "wool", "wb": "wool","pl":"polyester"
            }

fabric_subs = {"viscose":"viscose", "rayon":"viscose", "spandex":"elastane", "elastane":"elastane", "elastan":"elastane", "tane":"elastane", "alastane":"elastane", "polytrimethylane":"polyester",
               "elasane":"elastane", "elaste":"elastane", "flax":"linen", "linen": "linen", "nylon":"polyamide", "amid":"polyamide", "polia":"polyamide", "terell":"polyester", "elasto":"polyester", 
               "cotton": "cotton", "metal": "metallic", "acetate":"acetate", "modal":"modal", "cupro":"cotton", "modacrylic":"acrylic", "acry": "acrylic","silk":"silk",
               "poly":"polyester", "lurex":"polyester", "wool":"wool", "mohair":"wool", "cashmere":"wool", "merino":"wool", "alpaca":"wool", "seta":"silk", "sisal":"linen",
               "yak":"wool", "angora":"wool", "vicuna":"wool", "llama":"wool", "camel":"wool", "guanaco":"wool", "beaver":"wool", "crepe":"polyester", "satin":"polyester", 
               "korean organza":"polyester", "organza":"silk", "ramie":"linen", "suede":"leather", "leather":"leather", "goose":"feathers", "down":"feathers", "feather":"feathers",
               "bemberg":"cotton", "lycra": "elastane","lyra":"elastane", "acette":"acetate", "ctn":"cotton", "zamac":"metallic", "agnello":"wool", "denim":"cotton",
               "shearling":"leather", "glass":"glass", "polyester":"polyester", "circulose":"cotton", "mesh":"polyester", "lyocell":"lyocell", "tencel":"lyocell", "microtencel":"lyocell",
               "skin":"leather", "pwu":"polyester","lamb":"leather", "creme":"cotton", "elit":"acrylic", "jersey":"polyester","stretch":"polyester","laine":"wool","solvron":"wool",
               "crochet":"cotton","cord":"cotton", "poplin":"cotton","pliss":"polyester","nappa":"leather", "aluminium":"metallic","hemp":"linen","spa":"spandex",
               "brass":"metallic","wax":"cotton","steel":"metal","chaguar":"linen","taffeta":"polyester","econyl":"polyester","poli":"polyester","aluminum":"metallic", "elastan":"elastane", "arcy":"acrylic"
               }


def extract_from_s3(bucket_name=raw_bucket):
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
    
def care_labels(data, wash_labels=wash_labels):

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
    
    data["price"] = data['price'].str.replace(r"[$,]", "", regex=True)
    data["price"] = data["price"].astype("float")
    
    return data["price"]

def fabric_extractor(string, fiber_abbreviations=fiber_abb, fabric_substitutions=fabric_subs):

    """Mohair, Cashmere, Camelhair, Beaver, Angora, Merino, Vicuna, Llama, Yak, Guanaco, Lambswool, Sheepswool, 
    and Alpaca have been grouped under wool"""
    
    fabric_dict = {}
    new_dict = {}
    matches = re.findall(r"(\d+(?:\.\d+)?)%\s*([\w\s-]+?)(?=\d+%|$)", string)

    total_pct = 0
    for pct, fabric in matches:
        pct = float(pct)
        fabric = fabric.strip()
        if "trochus niloticus" in fabric:
            continue
            
        fabric_dict[fabric] = fabric_dict.get(fabric, 0) + pct

    for fab_string, pct in fabric_dict.items():

        if fab_string in fiber_abbreviations.keys():
            raw_fiber = fiber_abbreviations[fab_string]

        elif any(key in fab_string for key in fabric_substitutions):
            for key, val in fabric_substitutions.items():
                if key in fab_string:
                    raw_fiber = val
                    break
                    
        else:
            raw_fiber = "other"

        new_dict[raw_fiber] = new_dict.get(raw_fiber, 0) + pct
        total_pct += pct


    if total_pct > 100:
        for fabric in new_dict:
            new_dict[fabric] = round((new_dict[fabric] / total_pct) * 100)

    return new_dict
    

def composition_transform(data):

    dict_vec = DictVectorizer(sparse=False)

    data["composition"] = data["composition"].astype("str")
    data = data[data["composition"].str.contains("%", na=False, regex=False)]

    data.index = range(1, len(data) + 1)
    
    data["composition"] = data["composition"].str.replace(r'[^a-zA-Z(\d+(?:\.\d+)?)%\s]', "", regex=True)

    new_comp = data["composition"].apply(fabric_extractor).tolist()
    features = dict_vec.fit_transform(new_comp)
    fab_cols = dict_vec.get_feature_names_out()

    fab_df = pd.DataFrame(features, columns=fab_cols)
    fab_df.index = range(1, len(fab_df)+1)

    new_df = pd.concat([data.reset_index(drop=True), fab_df.reset_index(drop=True)], axis=1)
    new_df.drop(columns=["details", "composition"],inplace=True)

    return new_df

def transform_data(data):

    data.dropna(inplace=True)
    data = data.map(lambda x: x.lower() if isinstance(x, str) else x)

    data["price"] = price_transform(data)
    
    data["y"] = care_labels(data)

    data = composition_transform(data)
    links = data["link"].tolist()

    return links, data

def load_to_s3(links, df, bucket_name=historical_bucket):
    s3 = boto3.client("s3")

    try:
        historical_links = s3.get_object(Bucket=bucket_name, Key="historical_links.json")
        print("File found.")
        hist_links = historical_links["Body"]
        read_links = json.load(hist_links)
        read_links.extend(links)

        s3.put_object(Bucket=bucket_name, Body=json.dumps(links), Key="historical_links.json")
    except:
         
        print("No file found.")
        s3.put_object(Bucket=bucket_name, Body=json.dumps(links), Key="historical_links.json")

    try:
        historical_data = pd.read_csv(f's3://{bucket_name}/historical_data.csv')
        print("File found.")
        historical_data.index = range(1, len(historical_data)+1)
        new_df = pd.concat([historical_data.reset_index(drop=True), df.reset_index(drop=True)], axis=0)

        new_df.to_csv(f's3://{bucket_name}/historical_data.csv', index=False)

    except:
        print("No file found.")
        df.to_csv(f's3://{bucket_name}/historical_data.csv', index=False)

def main():
    extracted_data = extract_from_s3()
    links, df = transform_data(extracted_data)
    load_to_s3(links, df)

if __name__=="__main__":
    main()
