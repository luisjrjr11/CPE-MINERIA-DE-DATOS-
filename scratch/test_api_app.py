import requests
import json
import joblib

def test_artifacts():
    artifacts = joblib.load('modelo_credit_risk.pkl')
    print("Artifacts loaded successfully:", list(artifacts.keys()))
    print("Best model:", artifacts['best_model_name'])

if __name__ == '__main__':
    test_artifacts()
