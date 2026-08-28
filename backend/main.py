from fastapi import FastAPI, APIRouter
from mangum import Mangum
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import os
from inference import process

app = FastAPI()

class FabricInput(BaseModel):
    description: str
    price: int
    composition: dict[str, int]


origins = os.environ.get("ALLOWED_ORIGINS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origins],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/predict")
def predict(data: FabricInput):

    pos_proba = process(data.model_dump())
    if pos_proba:
        if pos_proba >= 0.5:
            message = "Machine Wash!"
        else: 
            message = "Don't machine wash!"
    else:
        message = "Error making prediction"        
    return {"prediction": message}

asgi_handler = Mangum(app)

def ping_handler(event, context):
    if event.get("source") == "aws.events":
        return {"statuscode": 200}
    return asgi_handler(event, context)