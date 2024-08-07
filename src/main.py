from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from typing import Annotated
from model import load_model, load_encoder
import pandas as pd

class Person(BaseModel):
    age: int
    job: str
    marital: str
    education: str
    balance: int
    housing: str
    duration: int
    campaign: int

app = FastAPI()

bearer = HTTPBearer()

ml_models = {}

@app.on_event("startup")
async def startup_event():
    ml_models["ohe"] = load_encoder()
    ml_models["models"] = load_model()

def get_username_for_token(token):
    if token == "abc123":
        return "pedro1"
    return ""


async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    token = credentials.credentials

    username = get_username_for_token(token)
    if username == "":
        raise HTTPException(status_code=401, detail="Invalid token")

    return {"username": username}

@app.get("/")
async def root():
    return "Model API is alive!"

@app.post("/predict")
async def predict(
    person: Annotated[
        Person,
        Body(
            examples=[
                {
                    "age": 42,
                    "job": "entrepreneur",
                    "marital": "married",
                    "education": "primary",
                    "balance": 558,
                    "housing": "yes",
                    "duration": 186,
                    "campaign": 2,
                }
            ],
        ),
    ],
    user=Depends(validate_token),
):
    ohe = ml_models["ohe"]
    model = ml_models["models"]

    person_t = ohe.transform(pd.DataFrame([person.dict()]))
    pred = model.predict(person_t)[0]

    return {
        "prediction": str(pred),
        "username": user["username"]
        }