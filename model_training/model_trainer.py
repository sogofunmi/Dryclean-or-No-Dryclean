import os
import optuna
import mlflow
import joblib
import pandas as pd
import xgboost as xgb
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import StandardScaler, RobustScaler
from sklearn.model_selection import train_test_split
from skbio.stats.composition import clr
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.feature_extraction import DictVectorizer


historical_bucket = os.environ.get("AWS_TRANSFORMED_DATA")
model_path = os.environ.get("MODEL_PATH", "all-MiniLM-L6-v2")
mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://mlflow_server:5000")

mlflow.set_tracking_uri(mlflow_uri)
mlflow.set_experiment("XGBoost Experiment")

client = mlflow.MlflowClient()

def data_split(bucket_name=historical_bucket):

    df = pd.read_csv(f"s3://{bucket_name}/historical_data.csv")

    price_prune = df.loc[((df["price"] < 200.0) & (df["y"]==0)) | ((df["price"] > 3000.0) & (df["y"]==0))]
    df.drop(price_prune.index, inplace=True)
    df.reset_index(inplace=True, drop=True)
    
    X_train_unscaled, X_test_unscaled, y_train, y_test = train_test_split(df.drop(["link", "y"], axis=1), 
                                                                              df["y"], test_size=0.3, random_state=40, stratify=df["y"])
    dict_vect = DictVectorizer(sparse=False)
    train_dicts = X_train_unscaled.drop(["title", "price"], axis=1).to_dict(orient="records")
    dict_vect.fit(train_dicts)                                                                  

    return X_train_unscaled, X_test_unscaled, y_train, y_test, dict_vect

def processing(X_train_unscaled, X_test_unscaled, model_path):
    
    embedding_model = SentenceTransformer(model_path, device="cpu")

    scaler = RobustScaler()
    emb_train = embedding_model.encode(X_train_unscaled["title"].tolist())
    emb_test = embedding_model.encode(X_test_unscaled["title"].tolist())

    scaled_price_train = scaler.fit_transform(X_train_unscaled[["price"]])
    scaled_price_test = scaler.transform(X_test_unscaled[["price"]])

    fabric_comp_train =  X_train_unscaled.drop(["price", "title"], axis=1)
    fabric_comp_test = X_test_unscaled.drop(["price", "title"], axis=1)
        
    X_train, X_test = clr_features(fabric_comp_train, fabric_comp_test)

    X_train["price"] = scaled_price_train
    X_test["price"] = scaled_price_test

    emb_train_df = pd.DataFrame(emb_train)
    emb_test_df = pd.DataFrame(emb_test)

    emb_train_df.index = range(len(emb_train_df))
    X_train = pd.concat([X_train, emb_train_df], axis=1)

    emb_test_df.index = range(len(emb_test_df))
    X_test = pd.concat([X_test, emb_test_df], axis=1)

        
    return X_train, X_test, scaler, embedding_model

def clr_features(train, test):
    train = (train / 100) + 0.005
    test = (test / 100) + 0.005

    components_train = clr(train)
    components_test = clr(test)

    cols = train.columns.tolist()
    components_train_df = pd.DataFrame(list(components_train), columns=cols)
    components_test_df = pd.DataFrame(list(components_test), columns=cols)

    return components_train_df, components_test_df

def XGB(X_train, y_train, X_test, y_test, scaler, dv, embedding_model, n_trials):
    
    joblib.dump(scaler, "scaler.pkl")
    joblib.dump(dv, "dict_vect.pkl")
    
    mlflow.xgboost.autolog(log_models=False)
    def objective(trial):
        
        params = {
                    "n_estimators": trial.suggest_int("n_estimators", 80, 700),
                    "max_depth": trial.suggest_int("max_depth", 3, 15),
                    "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.15, log=True)
                }

        with mlflow.start_run(nested=True):
            base_model = xgb.XGBClassifier(**params, eval_metric="aucpr", scale_pos_weight=6)
            base_model.fit(X_train, y_train)

            y_pred = base_model.predict(X_test)

            f1 = f1_score(y_test, y_pred)

            return f1

    try:
        prod_version = client.get_model_version_by_alias(name="XGBoost Model", alias="production")
        run_data = client.get_run(prod_version.run_id).data
        current_f1 = run_data.metrics.get("Best F1 Score", 0.0)

    except Exception:
        current_f1 = 0.0

    with mlflow.start_run():
        
        study = optuna.create_study(direction="maximize")
        study.optimize(objective, n_trials=n_trials)

        best_params = study.best_params

        mlflow.log_params({f"best_{k}": v for k, v in study.best_params.items()})
        mlflow.log_metric("Best F1 Score", study.best_value)

        best_model = xgb.XGBClassifier(**best_params, eval_metric="aucpr", scale_pos_weight=6)
        best_model.fit(X_train, y_train)
        y_pred_best = best_model.predict(X_test)

        precision = precision_score(y_test, y_pred_best)
        recall = recall_score(y_test, y_pred_best)

        mlflow.log_metric("Best Precision", precision)
        mlflow.log_metric("Best Recall", recall)

        model_info = mlflow.xgboost.log_model(best_model, name="Best_Model", registered_model_name="XGBoost Model")
        if study.best_value > current_f1:
            client.set_registered_model_alias(name="XGBoost Model", alias="production", version=model_info.registered_model_version)
        mlflow.log_artifact("scaler.pkl")
        mlflow.log_artifact("dict_vect.pkl")
        mlflow.sentence_transformers.log_model(embedding_model, name="Transformer", registered_model_name="Transformer")

def main():
    X_train_unscaled, X_test_unscaled, y_train, y_test, dict_vect = data_split()
    X_train, X_test, fitted_scaler, emb_model = processing(X_train_unscaled, X_test_unscaled, model_path=model_path)

    XGB(X_train, y_train, X_test, y_test, fitted_scaler, dict_vect, emb_model, n_trials=100)


if __name__ == "__main__":
    main()
