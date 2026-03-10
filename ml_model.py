import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

def predict_win():

    x=np.array([[1],[2],[3],[4],[5]])
    y=np.array([0.48,0.50,0.52,0.54,0.56])

    model=LinearRegression()

    model.fit(x,y)

    pred=model.predict([[6]])

    return round(float(pred[0]),2)
