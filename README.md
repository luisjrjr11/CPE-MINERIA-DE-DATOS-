# Minería de Datos Aplicada a la Evaluación de Riesgo Crediticio y Detección de Default en Microcréditos (CrediAvance)

Este repositorio contiene la implementación práctica completa del proyecto de Minería de Datos para la carrera de Tecnologías de la Información de la Universidad Estatal Amazónica (UEA).

## 📌 Descripción del Proyecto
El proyecto aborda la problemática del riesgo de impago (*default*) en la entidad microfinanciera **CrediAvance**. A través de técnicas de aprendizaje automático supervisado de clasificación binaria, se analiza el comportamiento histórico de 7,500 solicitudes de crédito para construir modelos predictivos capaces de estimar la probabilidad de morosidad y guiar la toma de decisiones comerciales.

## 🎯 Objetivos
1. **Explorar y caracterizar** el perfil socioeconómico y financiero de los solicitantes mediante análisis estadístico y visualización de datos.
2. **Construir y comparar** tres algoritmos de clasificación de distinta naturaleza (Regresión Logística, Árbol de Decisión y Random Forest) evaluando su capacidad discriminativa mediante exactitud, precisión, recall, F1-Score, AUC-ROC y Validación Cruzada Estratificada ($K=5$).
3. **Identificar las variables clave** que inciden en el default y desplegar un servicio web interactivo (Streamlit) y un backend en API REST (FastAPI) para scoring en tiempo real.

---

## 🛠️ Tecnologías Empleadas
- **Lenguaje:** Python 3.10+
- **Procesamiento de Datos:** `pandas`, `numpy`
- **Visualización:** `matplotlib`, `seaborn`
- **Machine Learning & Preprocesamiento:** `scikit-learn`, `scipy`, `joblib`
- **Backend & API REST:** `fastapi`, `uvicorn`, `pydantic`
- **Interfaz Web Interactiva:** `streamlit`

---

## 📂 Estructura del Proyecto

```text
c:\Users\Roland Bonilla\MINERIA DE DATOS 2\
├── data/
│   └── credit_risk_dataset.csv       # Dataset sintético depurado (7,500 registros)
├── figs/
│   ├── fig1_distribucion_monto.png   # Histograma del monto solicitado
│   ├── fig2_boxplot_ingresos.png     # Boxplot Ratio Cuota/Ingreso vs Default
│   ├── fig3_default_por_vivienda.png # Barplot Tasa de Default por Tipo de Trabajo
│   ├── fig4_curvas_roc.png           # Curvas ROC comparativas (3 modelos)
│   ├── fig5_matriz_confusion.png     # Matriz de confusión del mejor modelo
│   └── fig6_feature_importance.png   # Importancia de variables Top 10 (Random Forest)
├── generate_data.py                  # Script de generación de datos reproducibles
├── analysis.py                       # Pipeline principal de EDA, preprocessing, modelado y métricas
├── report_data.json                  # Exportación de métricas numéricas y estadísticas
├── modelo_credit_risk.pkl            # Modelo entrenado y escalador serializado
├── api.py                            # API REST desarrollada en FastAPI (/predict_credit)
├── app.py                            # Web App interactiva desarrollada en Streamlit
├── requirements.txt                  # Dependencias del proyecto
└── README.md                         # Documentación del repositorio
```

---

## ⚙️ Instalación y Ejecución

### 1. Clonar el repositorio e instalar dependencias:
```bash
pip install -r requirements.txt
```

### 2. Generar el dataset:
```bash
python generate_data.py
```

### 3. Ejecutar el pipeline de análisis y modelado:
```bash
python analysis.py
```

### 4. Desplegar la API REST (FastAPI):
```bash
uvicorn api:app --reload --port 8000
```
*Acceso a documentación Swagger UI:* `http://127.0.0.1:8000/docs`

### 5. Desplegar la Aplicación Web (Streamlit):
```bash
streamlit run app.py
```
*Acceso a la interfaz web:* `http://localhost:8501`

---

## 📊 Resultados Clave del Modelado

| Modelo | Accuracy | Precision | Recall | F1-Score | AUC-ROC | CV AUC-ROC ($\mu \pm \sigma$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Regresión Logística** (Mejor Modelo) | **0.9220** | **0.8419** | **0.7112** | **0.7710** | **0.9553** | **0.9557 ± 0.0050** |
| **Random Forest** | 0.8913 | 0.8476 | 0.5018 | 0.6304 | 0.9347 | 0.9359 ± 0.0043 |
| **Árbol de Decisión** | 0.8760 | 0.7725 | 0.4657 | 0.5811 | 0.8933 | 0.9019 ± 0.0090 |

**Variables de Mayor Peso Predictivo:**
1. `Ratio_Cuota_Ingreso` (Cuota mensual / Ingreso mensual)
2. `mora_maxima_historica_Sin_Mora` (Historial crediticio sin atrasos)
3. `Indice_Capacidad_Pago` ((Ingresos - Gastos) / Cuota)
4. `mora_maxima_historica_61_90_dias` (Atrasos severos previas)
5. `score_credito_buro` (Puntaje crediticio de buró)
