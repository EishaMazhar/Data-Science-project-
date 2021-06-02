from typing import Optional
from fastapi import FastAPI

from tensorflow import keras

app = FastAPI()


@app.get("/jd_salary_prediction")
def read_root(jd):

    model = keras.models.load_model('../../Models/NN_model')
    y = (model.predict([jd]))[0][0]

    return {"Predicted Salary": float(y)}

# @app.post("/ML_predictor")
# def read_root(jd):

#     model = keras.models.load_model('../../Models/NN_model')
#     y = (model.predict([jd]))[0][0]

#     return {"Predicted Salary": float(y)}