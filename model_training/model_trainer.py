import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import numpy as np


historical_bucket = os.environ.get("AWS_TRANSFORMED_DATA")


scaler = MinMaxScaler().set_output(transform="pandas")
pca = PCA(n_components=3)

def data_split(bucket_name=historical_bucket):
    df = pd.read_csv(f"s3://{bucket_name}/historical_data.csv")
    
    
    X_train_unscaled, X_test_unscaled, y_train, y_test = train_test_split(df.drop(["title", "link", "y"], axis=1), df["y"], test_size=0.3, random_state=42)

    return 

def processing(bucket_name=historical_bucket, scaler=scaler):

    embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = list(embedding_model.encode(df["title"].tolist()))
    

    scaled_price_train = scaler.fit_transform(X_train_unscaled["price"])
    scaled_price_test = scaler.transform(X_test_unscaled["price"])

    fabric_comp_train =  X_train_unscaled.drop(["price"], axis=1)
    fabric_comp_test = X_test_unscaled.drop(["price"], axis=1)
    
    X_train, X_test = pca_features(fabric_comp_train, fabric_comp_test)

    X_train["price"] = scaled_price_train.values
    X_test["price"] = scaled_price_test["price"].values

    emb_df = pd.DataFrame(embeddings)

    emb_train = emb_df.loc[scaled_train.index]
    emb_train.index = range(len(emb_train))
    X_train = pd.concat([X_train, emb_train], axis=1)

    emb_test = emb_df.loc[scaled_test.index]
    emb_test.index = range(len(emb_test))
    X_test = pd.concat([X_test, emb_test], axis=1)
    
    return X_train, X_test, y_train, y_test

def rclr_transformation(features):
    pass

def pca_features(train, test):
    pca = PCA(n_components=3)


    components_train = pca.fit_transform(rclr_transformation(train.drop(["price"])))
    components_test = pca.transform(rclr_transformation(test.drop(["price"])))

    components_train_df = pd.DataFrame(list(components_train), columns=["PC1", "PC2", "PC3"])
    components_test_df = pd.DataFrame(list(components_test), columns=["PC1", "PC2", "PC3"])

    return components_train_df, components_test_df


def train(X_train, X_test, y_train, y_test):
    pass

def main():
    X_train, X_test, y_train, y_test = processing()
    train(X_train, X_test, y_train, y_test)

if __name__ == "__main__":
    main()
