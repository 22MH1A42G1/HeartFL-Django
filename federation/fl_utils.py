import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd

FEATURE_COLUMNS = ['age','sex','cp','trestbps','chol','fbs','restecg','thalach','exang','oldpeak','slope','ca','thal']

def train_local_model(csv_path):
    df = pd.read_csv(csv_path)
    df.columns = [c.lower().strip() for c in df.columns]
    X = df[FEATURE_COLUMNS].fillna(df[FEATURE_COLUMNS].mean())
    y = df['target']
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    model = LogisticRegression(max_iter=200)
    model.fit(X_scaled, y)
    accuracy = model.score(X_scaled, y)
    weights = {
        'coef': model.coef_.tolist(),
        'intercept': model.intercept_.tolist(),
        'scaler_mean': scaler.mean_.tolist(),
        'scaler_scale': scaler.scale_.tolist(),
        'n_samples': len(df)
    }
    return weights, accuracy

def aggregate_models(hospital_weights_list):
    total_samples = sum(w['n_samples'] for w in hospital_weights_list)
    avg_coef = np.zeros_like(hospital_weights_list[0]['coef'])
    avg_intercept = np.zeros_like(hospital_weights_list[0]['intercept'])
    avg_mean = np.zeros_like(hospital_weights_list[0]['scaler_mean'])
    avg_scale = np.zeros_like(hospital_weights_list[0]['scaler_scale'])
    for w in hospital_weights_list:
        weight_factor = w['n_samples'] / total_samples
        avg_coef += np.array(w['coef']) * weight_factor
        avg_intercept += np.array(w['intercept']) * weight_factor
        avg_mean += np.array(w['scaler_mean']) * weight_factor
        avg_scale += np.array(w['scaler_scale']) * weight_factor
    return {
        'coef': avg_coef.tolist(),
        'intercept': avg_intercept.tolist(),
        'scaler_mean': avg_mean.tolist(),
        'scaler_scale': avg_scale.tolist()
    }

def predict_risk(global_weights, patient_features):
    coef = np.array(global_weights['coef'])
    intercept = np.array(global_weights['intercept'])
    mean = np.array(global_weights['scaler_mean'])
    scale = np.array(global_weights['scaler_scale'])
    X = np.array(patient_features).reshape(1, -1)
    X_scaled = (X - mean) / scale
    logit = np.dot(X_scaled, coef.T) + intercept
    prob = 1 / (1 + np.exp(-logit))
    return float(prob[0][0])
