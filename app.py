from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import numpy as np

# Define the expected input format
class FuelBlendInput(BaseModel):
    feature1: float
    feature2: float
    feature3: float
    feature4: float
    feature5: float
    feature6: float
    feature7: float
    feature8: float
    feature9: float
    feature10: float

app = FastAPI()

# Load model
model = joblib.load("fuel_blend_model.pkl")

@app.post("/predict")
def predict(data: FuelBlendInput):
    # Convert to numpy 2D array
    X = np.array([[data.feature1, data.feature2, data.feature3]])
    prediction = model.predict(X)
    return {"prediction": prediction.tolist()}
