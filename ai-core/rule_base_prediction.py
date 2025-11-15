from pydantic import BaseModel 
import pandas as pd 
import pickle
import warnings
import os
def extract_time(data):
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data['hour'] = data['timestamp'].dt.hour
    data['minute'] = data['timestamp'].dt.minute
    data['day'] = data['timestamp'].dt.day
    data['month'] = data['timestamp'].dt.month
    data = data.drop('timestamp', axis=1)
    return data

def predict(input: dict):
    """
    This tool is used for predict product status

    """
    data = pd.DataFrame([input])
    data = extract_time(data)
    import os
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    with open(model_path, 'rb') as f:
        saved = pickle.load(f)
     
    model = saved['model']
    preprocessor = saved['preprocessor']
    X_preprocessed = preprocessor.transform(data)
    predictions = model.predict(X_preprocessed)
    predictions = int(predictions[0])
    return predictions
