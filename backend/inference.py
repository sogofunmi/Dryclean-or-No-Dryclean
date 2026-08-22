import os
from sentence_transformers import SentenceTransformer
import pandas as pd
from skbio.stats.composition import clr



def process(response, scaler, dv, emb_model_path):
    df = pd.json_normalize(response)
    df.columns = df.columns.str.replace("composition.", "", regex=False)

    df = df.map(lambda x: x.lower() if isinstance(x, str) else x)
    embedding_model = SentenceTransformer(emb_model_path)

    descr = df["description"].iloc[0]
    emb = embedding_model.encode([descr])

    emb_df = pd.DataFrame(emb.tolist())

    scaled_price = scaler.transform(df[["price"]])
    dicts = df.drop(["description", "price"], axis=1).to_dict(orient="records")
    fabric = dv.transform(dicts)
    fabric = (fabric / 100) + 0.005
    fabric = clr(fabric)

    fab_cols = dv.get_feature_names_out()
    scaled_df = pd.DataFrame(list(fabric), columns=fab_cols)
    scaled_df["price"] = scaled_price
    scaled_df = pd.concat([scaled_df, emb_df], axis=1)

    return scaled_df
