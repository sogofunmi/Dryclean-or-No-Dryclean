from fastapi import FastAPI, APIRouter
from mangum import Mangum
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import mlflow
from inference import process
import joblib 
import os

app = FastAPI()

class FabricInput(BaseModel):
    description: str
    price: int
    composition: dict[str, int]

router = APIRouter(prefix="/api")

origins = os.environ.get("ALLOWED_ORIGINS", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mlflow_uri = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")

mlflow.set_tracking_uri(mlflow_uri)

model_name = "XGBoost Model"
alias = "production"

client = mlflow.MlflowClient()

model_uri = f"models:/{model_name}@{alias}"

model = mlflow.xgboost.load_model(model_uri)

prod_version = client.get_model_version_by_alias(name=model_name, alias=alias)
run_id = prod_version.run_id
scaler_path = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path="Best_Model/scaler.pkl")
dict_vect_path = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path="Best_Model/dict_vect.pkl")

scaler = joblib.load(scaler_path)
dict_vect = joblib.load(dict_vect_path)

emb_model_path = os.environ.get("MODEL_PATH", "all-MiniLM-L6-v2")

@router.get("/health")
def health_check():
    return {"status": "healthy"}

@router.post("/predict")
def predict(data: FabricInput):
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
    return {"prediction": message}


app.include_router(router)

handler = Mangum(app)