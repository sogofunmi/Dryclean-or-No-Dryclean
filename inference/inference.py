from skbio.stats.composition import clr

def load():
    pass

def process(df, scaler, dv):
    embedding_model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
    emb = embedding_model.encode(df["title"].tolist())
    emb_df = pd.DataFrame(emb)

    scaled_price = scaler.transform(df[["price"]])

    dicts = df.drop(["title", "price"], axis=1).to_dict(orient="records")
    fabric = dv.transform(dicts)
    
    fabric = (fabric / 100) + 0.005
    fabric = clr(fabric)

    fab_cols = dv.get_feature_names_out()
    scaled_df = pd.DataFrame(list(fabric), columns=fab_cols)

    scaled_df["price"] = scaled_price
    scaled_df = pd.concat([scaled_df, emb_df], axis=1)

    return scaled_df

def predict(df, model):
    y_pred = model.predict(df)

    return y_pred

def main():
    scaler, dv, model = load_model()
    X = process(df, scaler, dv)
    predict(X)

if __name__=="__main__":
    main()
