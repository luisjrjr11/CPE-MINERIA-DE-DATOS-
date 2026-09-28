import os
import joblib
import pandas as pd
import numpy as np
import streamlit as st

# Configuración de página de Streamlit
st.set_page_config(
    page_title="CrediAvance - Evaluador de Riesgo Crediticio",
    page_icon="💳",
    layout="wide"
)

# Cargar artefactos del modelo
@st.cache_resource
def load_model_artifacts():
    model_path = 'modelo_credit_risk.pkl'
    if not os.path.exists(model_path):
        return None
    return joblib.load(model_path)

artifacts = load_model_artifacts()

# Título y Encabezado
st.title("💳 Sistema de Evaluaci\u00f3n de Riesgo Crediticio - CrediAvance")
st.markdown("""
Esta aplicaci\u00f3n web interactiva utiliza un modelo predictivo de **Miner\u00eda de Datos (Regresi\u00f3n Log\u00edstica)** para evaluar el riesgo de *default* (incumplimiento de pago) en solicitudes de microcr\u00e9dito en tiempo real.
""")

if artifacts is None:
    st.error("⚠️ No se encontr\u00f3 el archivo `modelo_credit_risk.pkl`. Por favor ejecuta `analysis.py` primero.")
    st.stop()

model = artifacts['model']
scaler = artifacts['scaler']
feature_names = artifacts['feature_names']
num_cols = artifacts['num_cols']
cat_cols = artifacts['cat_cols']

# Formulario de entrada dividido en 3 columnas
st.subheader("📋 Datos de la Solicitud de Cr\u00e9dito")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 👤 Perfil Socioecon\u00f3mico")
    edad = st.number_input("Edad del Solicitante", min_value=18, max_value=80, value=35)
    genero = st.selectbox("G\u00e9nero", ["Masculino", "Femenino"])
    estado_civil = st.selectbox("Estado Civil", ["Soltero", "Casado", "Divorciado", "Union_Libre"])
    nivel_educativo = st.selectbox("Nivel Educativo", ["Secundaria", "T\u00e9cnico", "Tercer_Nivel", "Postgrado"])
    tipo_vivienda = st.selectbox("Tipo de Vivienda", ["Alquilada", "Propia_Hipotecada", "Propia_Libre", "Familiar"])
    tipo_trabajo = st.selectbox("Tipo de Trabajo", ["Independiente", "Dependiente_Privado", "Dependiente_Publico", "Informal"])
    antiguedad_laboral = st.number_input("Antig\u00fcedad Laboral (A\u00f1os)", min_value=0.0, max_value=40.0, value=4.5, step=0.5)

with col2:
    st.markdown("### 💰 Finanzas y Solicitud")
    ingreso_mensual = st.number_input("Ingreso Mensual (USD)", min_value=350.0, max_value=10000.0, value=850.0, step=50.0)
    monto_credito = st.number_input("Monto Solicitado (USD)", min_value=500.0, max_value=20000.0, value=3000.0, step=100.0)
    plazo_meses = st.selectbox("Plazo del Cr\u00e9dito (Meses)", [6, 12, 18, 24, 36, 48, 60], index=3)
    
    # Estimación automática de cuota a 18% anual
    tasa_m = 0.18 / 12
    cuota_est = (monto_credito * (tasa_m * (1 + tasa_m)**plazo_meses) / ((1 + tasa_m)**plazo_meses - 1))
    cuota_mensual = st.number_input("Cuota Mensual Estimada (USD)", min_value=10.0, max_value=3000.0, value=float(round(cuota_est, 2)), step=10.0)
    
    gastos_familiares_mensuales = st.number_input("Gastos Familiares Mensuales (USD)", min_value=100.0, max_value=5000.0, value=400.0, step=25.0)

with col3:
    st.markdown("### 📊 Historial Crediticio y Garant\u00eda")
    score_credito_buro = st.slider("Score de Bur\u00f3 de Cr\u00e9dito", min_value=300, max_value=850, value=680)
    num_creditos_previos = st.number_input("N\u00b0 de Cr\u00e9ditos Previos", min_value=0, max_value=15, value=2)
    creditos_previos_pagados_ok = st.number_input("Cr\u00e9ditos Pagados Puntualmente", min_value=0, max_value=num_creditos_previos, value=2)
    mora_maxima_historica = st.selectbox("Mora M\u00e1xima Hist\u00f3rica", ["Sin_Mora", "1_30_dias", "31_60_dias", "61_90_dias"])
    posee_garantia = st.selectbox("¿Posee Garant\u00eda?", ["Si", "No"])
    valor_garantia = st.number_input("Valor Estimado de Garant\u00eda (USD)", min_value=0.0, max_value=50000.0, value=4000.0 if posee_garantia == "Si" else 0.0, step=500.0)
    tarjeta_credito_activa = st.selectbox("¿Tiene Tarjeta de Cr\u00e9dito Activa?", ["Si", "No"])

st.markdown("---")

if st.button("📊 Evaluar Solicitud de Cr\u00e9dito", use_container_width=True, type="primary"):
    # Construir DataFrame de entrada
    raw_dict = {
        'edad': edad,
        'genero': genero,
        'estado_civil': estado_civil,
        'nivel_educativo': nivel_educativo,
        'tipo_vivienda': tipo_vivienda,
        'tipo_trabajo': tipo_trabajo,
        'antiguedad_laboral': antiguedad_laboral,
        'ingreso_mensual': ingreso_mensual,
        'monto_credito': monto_credito,
        'plazo_meses': plazo_meses,
        'cuota_mensual': cuota_mensual,
        'score_credito_buro': score_credito_buro,
        'num_creditos_previos': num_creditos_previos,
        'creditos_previos_pagados_ok': creditos_previos_pagados_ok,
        'mora_maxima_historica': mora_maxima_historica,
        'posee_garantia': posee_garantia,
        'valor_garantia': valor_garantia,
        'gastos_familiares_mensuales': gastos_familiares_mensuales,
        'tarjeta_credito_activa': tarjeta_credito_activa
    }
    
    df_in = pd.DataFrame([raw_dict])
    
    # Variables Derivadas
    ratio_ci = round(cuota_mensual / ingreso_mensual, 4)
    cap_pago = round((ingreso_mensual - gastos_familiares_mensuales) / (cuota_mensual + 1), 4)
    cob_gar = round(valor_garantia / (monto_credito + 1), 4)
    
    df_in['Ratio_Cuota_Ingreso'] = ratio_ci
    df_in['Indice_Capacidad_Pago'] = cap_pago
    df_in['Cobertura_Garantia'] = cob_gar
    
    # Preprocesamiento y Encoding
    df_encoded = pd.get_dummies(df_in, columns=cat_cols, drop_first=True)
    for col in feature_names:
        if col not in df_encoded.columns:
            df_encoded[col] = 0
    df_encoded = df_encoded[feature_names]
    
    df_encoded[num_cols] = scaler.transform(df_encoded[num_cols])
    
    prob_default = float(model.predict_proba(df_encoded.values)[0][1])
    
    st.subheader("🎯 Resultado del Diagn\u00f3stico de Riesgo")
    
    m_col1, m_col2, m_col3 = st.columns(3)
    m_col1.metric("Probabilidad de Default", f"{prob_default * 100:.1f}%")
    m_col2.metric("Ratio Cuota / Ingreso", f"{ratio_ci * 100:.1f}%")
    m_col3.metric("\u00cdndice Capacidad de Pago", f"{cap_pago:.2f}x")
    
    st.markdown("### 📋 Dictamen de Evaluaci\u00f3n Commercial")
    
    if prob_default < 0.20:
        st.success(f"✅ **APROBADO AUTOM\u00c1TICO (Riesgo Bajo - {prob_default*100:.1f}%)**")
        st.info("💡 **Recomendaci\u00f3n:** El cliente presenta un perfil financiero s\u00f3lido. Desembolso inmediato sugerido.")
    elif prob_default < 0.50:
        st.warning(f"⚠️ **REVISI\u00d3N MANUAL (Riesgo Moderado - {prob_default*100:.1f}%)**")
        st.info("💡 **Recomendaci\u00f3n:** Se sugiere solicitar verificaci\u00f3n de ingresos o incrementar la cobertura de garant\u00eda antes de aprobar.")
    else:
        st.error(f"🚨 **RECHAZADO AUTOM\u00c1TICO (Riesgo Alto - {prob_default*100:.1f}%)**")
        st.info("💡 **Recomendaci\u00f3n:** Elevado riesgo de morosidad. Reestructurar monto/plazo o denegar la solicitud.")
