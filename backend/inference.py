import os
import pandas as pd
from skbio.stats.composition import clr

model = None
scaler = None
dict_vect = None
embedding_model = None
artifacts_loaded = False

def load_artifacts():
    global model, scaler, dict_vect, artifacts_loaded, embedding_model
    if artifacts_loaded:
        return
    import mlflow
    import joblib
    from sentence_transformers import SentenceTransformer
    mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI")
    if not mlflow_uri or "localhost" in mlflow_uri:
        raise RuntimeError("MLFLOW_TRACKING_URI is unset or pointing to localhost!")

    mlflow.set_tracking_uri(mlflow_uri)
    model_name = "XGBoost Model"
    alias = "production"

    client = mlflow.MlflowClient()
    model_uri = f"models:/{model_name}@{alias}"
    model = mlflow.xgboost.load_model(model_uri)

    prod_version = client.get_model_version_by_alias(name=model_name, alias=alias)
    run_id = prod_version.run_id

    scaler_path = mlflow.artifacts.download_artifacts(
        run_id=run_id, artifact_path="scaler.pkl", dst_path="/tmp")
    dict_vect_path = mlflow.artifacts.download_artifacts(
        run_id=run_id, artifact_path="dict_vect.pkl", dst_path="/tmp")

    scaler = joblib.load(scaler_path)
    dict_vect = joblib.load(dict_vect_path)
    model_path = os.environ.get("MODEL_PATH", "all-MiniLM-L6-v2")
    embedding_model = SentenceTransformer(model_path)
    artifacts_loaded = True


def process(response):

    load_artifacts()
    if model is None or scaler is None:
        return {"error": "Model artifacts failed to load."}

    df = pd.json_normalize(response)
    df.columns = df.columns.str.replace("composition.", "", regex=False)

    df = df.map(lambda x: x.lower() if isinstance(x, str) else x)

    descr = df["description"].iloc[0]
    emb = embedding_model.encode([descr])

    emb_df = pd.DataFrame(emb.tolist())

    scaled_price = scaler.transform(df[["price"]])
    dicts = df.drop(["description", "price"], axis=1).to_dict(orient="records")
    fabric = dict_vect.transform(dicts)
    fabric = (fabric / 100) + 0.005
    fabric = clr(fabric)

    fab_cols = dict_vect.get_feature_names_out()
    scaled_df = pd.DataFrame(list(fabric), columns=fab_cols)
    scaled_df["price"] = scaled_price
    scaled_df = pd.concat([scaled_df, emb_df], axis=1)

    return scaled_df
