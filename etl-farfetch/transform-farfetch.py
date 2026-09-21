import boto3
import os
import pandas as pd
import json
import re
from sklearn.feature_extraction import DictVectorizer

farfetch_bucket = os.environ.get("AWS_FARFETCH_DATA", "farfetch-bucket")
historical_bucket = os.environ.get("AWS_TRANSFORMED_DATA", "sogo-transformed-bucket")

s3 = boto3.client("s3")

FIBER_ABBR = {"ac": "acetate", "ca":"acetate", "cmd": "modal", "co": "cotton", "cta": "acetate",
            "cu": "cotton", "cup": "cotton", "cv": "viscose", "ea": "elastane", "el": "elastane",
            "hl": "linen", "li": "linen", "ma": "acrylic", "mo": "modal", "ny": "polyamide",
            "pe": "polyester", "pes": "polyester", "pet": "polyester", "pm": "polyester", "pu": "polyester",
            "ra": "linen", "se": "silk", "ta": "acetate", "vi": "viscose", "wa": "wool", "wg": "wool", "wk": "wool",
            "wl": "wool", "wm": "wool", "wp": "wool", "ws": "wool", "wy": "wool", "wv": "wool", "wo": "wool",
            "wu": "wool", "wb": "wool","pl":"polyester"
            }

FABRIC_SUBS = {"viscose":"viscose", "rayon":"viscose", "spandex":"elastane", "elastane":"elastane", "elastan":"elastane", "tane":"elastane", "alastane":"elastane", "polytrimethylane":"polyester",
               "elasane":"elastane", "elastae":"elastane","elaste":"elastane", "flax":"linen", "linen": "linen", "nylon":"polyamide", "amid":"polyamide", "polia":"polyamide", "terell":"polyester", "elasto":"polyester", 
               "cotton": "cotton", "acetate":"acetate", "modal":"modal", "cupro":"cotton", "modacrylic":"acrylic", "acry": "acrylic","silk":"silk",
               "poly":"polyester", "lurex":"polyester", "wool":"wool", "mohair":"wool", "cashmere":"wool", "merino":"wool", "alpaca":"wool", "seta":"silk", "sisal":"linen",
               "yak":"wool", "angora":"wool", "vicuna":"wool", "llama":"wool", "camel":"wool", "guanaco":"wool", "beaver":"wool", "crepe":"polyester", "satin":"polyester", 
               "korean organza":"polyester", "organza":"silk", "ramie":"linen", "suede":"leather", "leather":"leather",
               "bemberg":"cotton", "lycra": "elastane","lyra":"elastane", "acette":"acetate", "ctn":"cotton", "agnello":"wool", "denim":"cotton",
               "shearling":"leather", "polyester":"polyester", "circulose":"cotton", "mesh":"polyester", "lyocell":"lyocell", "tencel":"lyocell", "microtencel":"lyocell",
               "skin":"leather", "pwu":"polyester","lamb":"leather", "hide":"leather", "creme":"cotton", "elit":"acrylic", "jersey":"polyester","stretch":"polyester","laine":"wool","solvron":"wool",
               "crochet":"cotton","cord":"cotton", "poplin":"cotton","pliss":"polyester","nappa":"leather","hemp":"linen","spa":"elastane",
               "wax":"cotton","chaguar":"linen","taffeta":"polyester","econyl":"polyester","poli":"polyester", "elastan":"elastane", "arcy":"acrylic"
               }


def extract_from_s3():
    s3 = boto3.client("s3")
    
    response = s3.list_objects_v2(Bucket=farfetch_bucket)
    files = response.get("Contents", [])

    if files:
        recent_file = sorted(files, key=lambda x: x["LastModified"])[-1]
        file_key = recent_file["Key"]
        file = s3.get_object(Bucket=farfetch_bucket, Key=file_key)

        raw_file = file["Body"]
        read_file = json.load(raw_file)

        data = pd.DataFrame(read_file)
        data.index = range(1, len(data) + 1)
        
        return data
    else:
        print("No file found in bucket")

def fabric_extractor(string):
    
    fabric_dict = {}
    total_pct = 0

    matches = re.findall(r"([a-zA-Z\s]+)\s*(\d+(?:\.\d+)?)%", string)

    for fabric, pct in matches:
        fabric = fabric.strip()
        pct = float(pct)

        if any (key in fabric for key in FABRIC_SUBS):
            for key, value in FABRIC_SUBS.items():
                if key in fabric:
                    fabric = value
                    break
        elif fabric in FIBER_ABBR.keys():
            fabric = FIBER_ABBR[fabric]
        else:
            fabric = "other"
        
        fabric_dict[fabric] = fabric_dict.get(fabric, 0) + pct
        total_pct += pct
    if total_pct > 100:
        for fabric in fabric_dict:
            fabric_dict[fabric] = round((fabric_dict[fabric] / total_pct)*100)
    return fabric_dict

def composition_transform(data):
    dict_vec = DictVectorizer(sparse=False)

    data["composition"] = data["composition"].astype("str").replace(r"[^(\d+(?:\.\d+)?)a-zA-Z%\s]", "", regex=True)
    data = data.map(lambda x: x.lower() if isinstance(x, str) else x)

    composition = data["composition"].apply(fabric_extractor).tolist()
    features = dict_vec.fit_transform(composition)
    fab_cols = dict_vec.get_feature_names_out()

    fab_df = pd.DataFrame(features, columns=fab_cols)
    fab_df.index = range(1, len(fab_df)+1)

    new_df = pd.concat([data.reset_index(drop=True), fab_df.reset_index(drop=True)], axis=1)
    new_df["total"] = fab_df.sum(axis=1)

    less_100 = new_df.loc[new_df["total"]<100.0]

    new_df.drop(less_100.index, inplace=True)
    new_df.drop(columns=["composition", "total"],inplace=True)

    new_df.index = range(1, len(new_df) + 1)

    return new_df

def transform(data):
    links = data["link"].tolist()

    data.drop_duplicates(subset="title", inplace=True)
    data.dropna(inplace=True)

    data["price"] = data["price"].replace(r"[$,]", "", regex=True).astype("float")
    data["care"] = 1
    data.rename(columns={"care": "y"}, inplace=True)

    data = composition_transform(data)

    return links, data

def load_to_s3(links, data):
    try:
        farfetch_links = s3.get_object(Bucket=historical_bucket, key="farfetch_links.json")
        loaded_links = farfetch_links["Body"]

        read_links = json.load(loaded_links)
        read_links.extend(links)

        s3.put_object(Bucket=historical_bucket, Body=json.dumps(read_links), key="farfetch_links.json")
    except:
        print("No file found.")
        s3.put_object(Bucket=historical_bucket, Body=json.dumps(links), Key="farfetch_links.json")

    try:
        farfetch_data = pd.read_csv(f"s3://{historical_bucket}/farfetch_data.csv")
        print("File found.")
        
        new_df = pd.concat([farfetch_data.reset_index(drop=True), data.reset_index(drop=True)], axis=0)

        new_df.to_csv(f's3://{historical_bucket}/farfetch_data.csv', index=False)
    except:
        print("No file found.")
        data.to_csv(f's3://{historical_bucket}/farfetch_data.csv', index=False)

def main():
    extracted_data = extract_from_s3()
    links, df = transform(extracted_data)
    load_to_s3(links, df)

if __name__=="__main__":
    main()