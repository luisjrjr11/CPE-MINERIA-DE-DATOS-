import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, roc_curve, confusion_matrix)

def run_analysis():
    # Configuración de estilos visuales
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({'font.size': 11, 'figure.autolayout': True})
    
    # 1. Cargar datos
    data_path = os.path.join('data', 'credit_risk_dataset.csv')
    df_raw = pd.read_csv(data_path)
    
    total_rows_raw = len(df_raw)
    total_cols = len(df_raw.columns)
    
    # 2. Diagnóstico de calidad de datos (Nulos y duplicados)
    nulls_count = df_raw.isnull().sum().to_dict()
    nulls_pct = (df_raw.isnull().sum() / total_rows_raw * 100).round(2).to_dict()
    
    dup_count = int(df_raw.duplicated().sum())
    dup_pct = round(dup_count / total_rows_raw * 100, 2)
    
    # Limpieza
    df_clean = df_raw.drop_duplicates().copy()
    total_rows_clean = len(df_clean)
    
    # Imputación de nulos en gastos_familiares_mensuales por la mediana
    mediana_gastos = df_clean['gastos_familiares_mensuales'].median()
    df_clean['gastos_familiares_mensuales'] = df_clean['gastos_familiares_mensuales'].fillna(mediana_gastos)
    
    # Estadísticas descriptivas clave
    num_cols_desc = ['edad', 'antiguedad_laboral', 'ingreso_mensual', 'monto_credito', 
                     'plazo_meses', 'cuota_mensual', 'score_credito_buro', 'gastos_familiares_mensuales', 'valor_garantia']
    
    desc_stats = {}
    for col in num_cols_desc:
        desc_stats[col] = {
            'count': int(df_clean[col].count()),
            'mean': float(round(df_clean[col].mean(), 2)),
            'std': float(round(df_clean[col].std(), 2)),
            'min': float(round(df_clean[col].min(), 2)),
            '25%': float(round(df_clean[col].quantile(0.25), 2)),
            '50%': float(round(df_clean[col].median(), 2)),
            '75%': float(round(df_clean[col].quantile(0.75), 2)),
            'max': float(round(df_clean[col].max(), 2))
        }
        
    # 3. Feature Engineering (Variables Derivadas)
    df_clean['Ratio_Cuota_Ingreso'] = (df_clean['cuota_mensual'] / df_clean['ingreso_mensual']).round(4)
    df_clean['Indice_Capacidad_Pago'] = ((df_clean['ingreso_mensual'] - df_clean['gastos_familiares_mensuales']) / (df_clean['cuota_mensual'] + 1)).round(4)
    df_clean['Cobertura_Garantia'] = (df_clean['valor_garantia'] / (df_clean['monto_credito'] + 1)).round(4)
    
    # 4. Visualizaciones Exploratorias
    # Figura 1: Distribución del monto de crédito
    plt.figure(figsize=(8, 4.5))
    sns.histplot(df_clean['monto_credito'], kde=True, color='#1f77b4', bins=30)
    plt.title('Distribución del Monto de Crédito Solicitado (USD)', fontsize=13, fontweight='bold')
    plt.xlabel('Monto del Crédito (USD)')
    plt.ylabel('Frecuencia (N° de Solicitantes)')
    plt.savefig(os.path.join('figs', 'fig1_distribucion_monto.png'), dpi=300)
    plt.close()
    
    # Figura 2: Boxplot Ratio Cuota/Ingreso según Default
    plt.figure(figsize=(8, 5))
    sns.boxplot(x='default', y='Ratio_Cuota_Ingreso', data=df_clean, palette=['#2ca02c', '#d62728'], hue='default', legend=False)
    plt.title('Diagrama de Cajas: Ratio Cuota/Ingreso por Estado de Default', fontsize=13, fontweight='bold')
    plt.xlabel('Estado de Default (0: Puntual, 1: Default)')
    plt.ylabel('Ratio Cuota / Ingreso Mensual')
    plt.xticks([0, 1], ['Puntual (0)', 'Default (1)'])
    plt.savefig(os.path.join('figs', 'fig2_boxplot_ingresos.png'), dpi=300)
    plt.close()
    
    # Figura 3: Tasa de Default por Tipo de Trabajo
    plt.figure(figsize=(8.5, 4.5))
    def_work = df_clean.groupby('tipo_trabajo')['default'].mean().reset_index()
    def_work['default_pct'] = def_work['default'] * 100
    sns.barplot(x='tipo_trabajo', y='default_pct', data=def_work, palette='Blues_r', hue='tipo_trabajo', legend=False)
    plt.title('Porcentaje de Default según el Tipo de Trabajo del Solicitante', fontsize=13, fontweight='bold')
    plt.xlabel('Tipo de Trabajo')
    plt.ylabel('Porcentaje de Default (%)')
    for i, row in def_work.iterrows():
        plt.text(i, row['default_pct'] + 0.5, f"{row['default_pct']:.1f}%", ha='center', fontweight='bold')
    plt.savefig(os.path.join('figs', 'fig3_default_por_vivienda.png'), dpi=300)
    plt.close()

    # 5. Preprocesamiento para Modelado
    X_df = df_clean.drop(columns=['id_cliente', 'default'])
    y = df_clean['default'].values
    
    cat_cols = ['genero', 'estado_civil', 'nivel_educativo', 'tipo_vivienda', 
                'tipo_trabajo', 'mora_maxima_historica', 'posee_garantia', 'tarjeta_credito_activa']
    num_cols = [c for c in X_df.columns if c not in cat_cols]
    
    # One-Hot Encoding
    X_encoded = pd.get_dummies(X_df, columns=cat_cols, drop_first=True)
    feature_names = X_encoded.columns.tolist()
    
    # Escalado de numéricas
    scaler = StandardScaler()
    X_encoded[num_cols] = scaler.fit_transform(X_encoded[num_cols])
    
    X = X_encoded.values
    
    # Partición 80/20 Estratificada
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    # 6. Definición y Entrenamiento de Modelos
    models = {
        'Regresión Logística': LogisticRegression(solver='lbfgs', C=1.0, max_iter=1000, random_state=42),
        'Árbol de Decisión': DecisionTreeClassifier(criterion='gini', max_depth=6, min_samples_leaf=20, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=8, criterion='gini', random_state=42)
    }
    
    model_test_metrics = {}
    model_cv_metrics = {}
    trained_models = {}
    
    cv_strat = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # Curvas ROC data
    roc_data = {}
    
    for name, clf in models.items():
        # Fit on train
        clf.fit(X_train, y_train)
        trained_models[name] = clf
        
        # Test evaluation
        y_pred = clf.predict(X_test)
        y_prob = clf.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_prob)
        
        fpr, tpr, _ = roc_curve(y_test, y_prob)
        roc_data[name] = (fpr, tpr, auc)
        
        model_test_metrics[name] = {
            'Accuracy': float(round(acc, 4)),
            'Precision': float(round(prec, 4)),
            'Recall': float(round(rec, 4)),
            'F1-Score': float(round(f1, 4)),
            'AUC-ROC': float(round(auc, 4))
        }
        
        # Cross-validation
        scoring = ['accuracy', 'f1', 'roc_auc']
        cv_res = cross_validate(clf, X_train, y_train, cv=cv_strat, scoring=scoring)
        
        model_cv_metrics[name] = {
            'CV Accuracy Mean': float(round(cv_res['test_accuracy'].mean(), 4)),
            'CV Accuracy Std': float(round(cv_res['test_accuracy'].std(), 4)),
            'CV F1 Mean': float(round(cv_res['test_f1'].mean(), 4)),
            'CV F1 Std': float(round(cv_res['test_f1'].std(), 4)),
            'CV AUC-ROC Mean': float(round(cv_res['test_roc_auc'].mean(), 4)),
            'CV AUC-ROC Std': float(round(cv_res['test_roc_auc'].std(), 4))
        }
        
    # Figura 4: Curvas ROC Comparativas
    plt.figure(figsize=(8, 6))
    colors = {'Regresión Logística': '#1f77b4', 'Árbol de Decisión': '#ff7f0e', 'Random Forest': '#2ca02c'}
    for name in models.keys():
        fpr, tpr, auc = roc_data[name]
        plt.plot(fpr, tpr, label=f"{name} (AUC = {auc:.3f})", color=colors[name], lw=2)
    plt.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Azar (AUC = 0.500)')
    plt.title('Curvas ROC Comparativas de los Modelos Evaluados', fontsize=13, fontweight='bold')
    plt.xlabel('Tasa de Falsos Positivos (False Positive Rate)')
    plt.ylabel('Tasa de Verdaderos Positivos (True Positive Rate)')
    plt.legend(loc='lower right', frameon=True)
    plt.savefig(os.path.join('figs', 'fig4_curvas_roc.png'), dpi=300)
    plt.close()
    
    # Seleccionar el mejor modelo basado en AUC-ROC
    best_model_name = max(model_test_metrics, key=lambda k: model_test_metrics[k]['AUC-ROC'])
    best_model = trained_models[best_model_name]
    
    # Figura 5: Matriz de Confusión del Mejor Modelo
    plt.figure(figsize=(6, 5))
    y_pred_best = best_model.predict(X_test)
    cm = confusion_matrix(y_test, y_pred_best)
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', cbar=False,
                xticklabels=['Puntual (0)', 'Default (1)'],
                yticklabels=['Puntual (0)', 'Default (1)'])
    plt.title(f'Matriz de Confusión - {best_model_name}', fontsize=12, fontweight='bold')
    plt.xlabel('Predicción del Modelo')
    plt.ylabel('Valor Real (Ground Truth)')
    plt.savefig(os.path.join('figs', 'fig5_matriz_confusion.png'), dpi=300)
    plt.close()
    
    # Figura 6: Importancia de Variables (Random Forest)
    rf_clf = trained_models['Random Forest']
    importances = rf_clf.feature_importances_
    indices = np.argsort(importances)[::-1][:10] # Top 10
    
    top_features = [feature_names[i] for i in indices]
    top_importances = importances[indices]
    
    plt.figure(figsize=(9, 5))
    sns.barplot(x=top_importances, y=top_features, palette='viridis', hue=top_features, legend=False)
    plt.title('Importancia de Variables (Top 10 - Random Forest)', fontsize=13, fontweight='bold')
    plt.xlabel('Importancia Relativa (Gini Impurity Decrease)')
    plt.ylabel('Variable')
    plt.savefig(os.path.join('figs', 'fig6_feature_importance.png'), dpi=300)
    plt.close()
    
    # Guardar reporte JSON
    report_dict = {
        'total_rows_raw': total_rows_raw,
        'total_rows_clean': total_rows_clean,
        'nulls_count': nulls_count,
        'nulls_pct': nulls_pct,
        'dup_count': dup_count,
        'dup_pct': dup_pct,
        'descriptive_stats': desc_stats,
        'test_metrics': model_test_metrics,
        'cv_metrics': model_cv_metrics,
        'best_model': best_model_name,
        'top_10_features': top_features,
        'top_10_importances': [float(round(imp, 4)) for imp in top_importances]
    }
    
    with open('report_data.json', 'w', encoding='utf-8') as f:
        json.dump(report_dict, f, indent=4, ensure_ascii=False)
        
    # Exportar modelo serializado .pkl
    artifact_payload = {
        'model': best_model,
        'scaler': scaler,
        'feature_names': feature_names,
        'num_cols': num_cols,
        'cat_cols': cat_cols,
        'best_model_name': best_model_name
    }
    joblib.dump(artifact_payload, 'modelo_credit_risk.pkl')
    print("Análisis y entrenamiento completados satisfactoriamente.")
    print(f"Mejor modelo seleccionado: {best_model_name}")
    print(f"Métricas en Test de {best_model_name}: {model_test_metrics[best_model_name]}")

if __name__ == '__main__':
    run_analysis()
