from fastapi import FastAPI, APIRouter
from mangum import Mangum
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import mlflow
from inference import process
import joblib 
import os
from contextlib import asynccontextmanager

app = FastAPI()

class FabricInput(BaseModel):
    description: str
    price: int
    composition: dict[str, int]

router = APIRouter(prefix="/api")

origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"],
)


model = None
scaler = None
dict_vect = None
emb_model_path = os.environ.get("MODEL_PATH", "all-MiniLM-L6-v2")
_artifacts_loaded = False

def load_artifacts():
    global model, scaler, dict_vect, _artifacts_loaded
    if _artifacts_loaded:
        return

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
        run_id=run_id, artifact_path="Best_Model/scaler.pkl", dst_path="/tmp"
    )
    dict_vect_path = mlflow.artifacts.download_artifacts(
        run_id=run_id, artifact_path="Best_Model/dict_vect.pkl", dst_path="/tmp"
    )

    scaler = joblib.load(scaler_path)
    dict_vect = joblib.load(dict_vect_path)
    _artifacts_loaded = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.post("/predict")
def predict(data: FabricInput):

    if model is None or scaler is None:
        return {"error": "Model artifacts failed to load."}

    raw_data = data.model_dump()
    scaled_df = process(raw_data, scaler, dict_vect, emb_model_path)
    
    prediction = model.predict_proba(scaled_df)
    pos_proba = prediction[0][1]

    if pos_proba:
        if pos_proba >= 0.5:
            message = "Machine Wash!"
        else: 
            message = "Don't machine wash!"
    else:
        message = "Error making prediction"        
    #return {"prediction": message}
    return JSONResponse(
        content={"prediction": message},
        headers={"Access-Control-Allow-Origin": "https://machine-wash-or-not.com"}
    )

app.include_router(router)

handler = Mangum(app, lifespan="off", api_gateway_base_path="/api")