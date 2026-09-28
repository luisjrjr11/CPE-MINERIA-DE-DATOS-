import os
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# 1. Cargar artefactos serializados
MODEL_PATH = 'modelo_credit_risk.pkl'
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"No se encontró el archivo del modelo: {MODEL_PATH}")

artifacts = joblib.load(MODEL_PATH)
model = artifacts['model']
scaler = artifacts['scaler']
feature_names = artifacts['feature_names']
num_cols = artifacts['num_cols']
cat_cols = artifacts['cat_cols']

# 2. Inicializar FastAPI
app = FastAPI(
    title="API REST de Scoring de Riesgo Crediticio - CrediAvance",
    description="Servicio backend para la evaluación predictiva de default en solicitudes de microcrédito.",
    version="1.0.0"
)

# 3. Modelo de entrada Pydantic
class CreditoSolicitud(BaseModel):
    edad: int = Field(..., ge=18, le=80, example=35)
    genero: str = Field(..., example="Masculino")
    estado_civil: str = Field(..., example="Casado")
    nivel_educativo: str = Field(..., example="Tercer_Nivel")
    tipo_vivienda: str = Field(..., example="Propia_Hipotecada")
    tipo_trabajo: str = Field(..., example="Dependiente_Privado")
    antiguedad_laboral: float = Field(..., ge=0, example=4.5)
    ingreso_mensual: float = Field(..., ge=350, example=850.0)
    monto_credito: float = Field(..., ge=500, example=3000.0)
    plazo_meses: int = Field(..., ge=6, le=60, example=24)
    cuota_mensual: float = Field(..., ge=10, example=150.0)
    score_credito_buro: int = Field(..., ge=300, le=850, example=680)
    num_creditos_previos: int = Field(..., ge=0, example=2)
    creditos_previos_pagados_ok: int = Field(..., ge=0, example=2)
    mora_maxima_historica: str = Field(..., example="Sin_Mora")
    posee_garantia: str = Field(..., example="Si")
    valor_garantia: float = Field(..., ge=0, example=4000.0)
    gastos_familiares_mensuales: float = Field(..., ge=100, example=400.0)
    tarjeta_credito_activa: str = Field(..., example="Si")

@app.get("/")
def home():
    return {
        "mensaje": "API de Evaluación de Riesgo Crediticio - CrediAvance activa",
        "modelo_vigente": artifacts['best_model_name'],
        "endpoint_prediccion": "/predict_credit"
    }

@app.post("/predict_credit")
def predict_credit(solicitud: CreditoSolicitud):
    try:
        # Convertir entrada Pydantic a DataFrame
        raw_dict = solicitud.model_dump()
        df_in = pd.DataFrame([raw_dict])
        
        # Feature Engineering (Variables Derivadas)
        df_in['Ratio_Cuota_Ingreso'] = (df_in['cuota_mensual'] / df_in['ingreso_mensual']).round(4)
        df_in['Indice_Capacidad_Pago'] = ((df_in['ingreso_mensual'] - df_in['gastos_familiares_mensuales']) / (df_in['cuota_mensual'] + 1)).round(4)
        df_in['Cobertura_Garantia'] = (df_in['valor_garantia'] / (df_in['monto_credito'] + 1)).round(4)
        
        # Encoding categórico alineado con el entrenamiento
        df_encoded = pd.get_dummies(df_in, columns=cat_cols, drop_first=True)
        
        # Reindexar columnas para garantizar coincidencia exacta con el modelo
        for col in feature_names:
            if col not in df_encoded.columns:
                df_encoded[col] = 0
        df_encoded = df_encoded[feature_names]
        
        # Escalado de variables numéricas
        df_encoded[num_cols] = scaler.transform(df_encoded[num_cols])
        
        # Predicción
        prob_default = float(model.predict_proba(df_encoded.values)[0][1])
        pred_clase = int(model.predict(df_encoded.values)[0])
        
        # Dictamen de negocio
        if prob_default < 0.20:
            dictamen = "APROBADO AUTOMÁTICO (Riesgo Bajo)"
            color = "Verde"
        elif prob_default < 0.50:
            dictamen = "REVISIÓN MANUAL (Riesgo Moderado)"
            color = "Amarillo"
        else:
            dictamen = "RECHAZADO AUTOMÁTICO (Riesgo Alto / Morosidad Probable)"
            color = "Rojo"
            
        return {
            "probabilidad_default": round(prob_default, 4),
            "probabilidad_default_pct": f"{round(prob_default * 100, 2)}%",
            "prediccion_binaria": pred_clase,
            "dictamen_comercial": dictamen,
            "categoria_riesgo": color,
            "ratio_cuota_ingreso": float(df_in['Ratio_Cuota_Ingreso'].iloc[0]),
            "indice_capacidad_pago": float(df_in['Indice_Capacidad_Pago'].iloc[0])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
