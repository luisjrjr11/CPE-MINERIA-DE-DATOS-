import os
import numpy as np
import pandas as pd

def generate_credit_dataset():
    np.random.seed(42)
    n = 7500
    
    id_cliente = [f"CLI-{10001 + i}" for i in range(n)]
    genero = np.random.choice(['Masculino', 'Femenino'], size=n, p=[0.52, 0.48])
    edad = np.random.randint(18, 68, size=n)
    estado_civil = np.random.choice(['Soltero', 'Casado', 'Divorciado', 'Union_Libre'], size=n, p=[0.35, 0.45, 0.10, 0.10])
    nivel_educativo = np.random.choice(['Secundaria', 'Técnico', 'Tercer_Nivel', 'Postgrado'], size=n, p=[0.40, 0.30, 0.25, 0.05])
    tipo_vivienda = np.random.choice(['Alquilada', 'Propia_Hipotecada', 'Propia_Libre', 'Familiar'], size=n, p=[0.35, 0.25, 0.25, 0.15])
    tipo_trabajo = np.random.choice(['Independiente', 'Dependiente_Privado', 'Dependiente_Publico', 'Informal'], size=n, p=[0.38, 0.37, 0.15, 0.10])
    antiguedad_laboral = np.random.exponential(scale=5.0, size=n).round(1)
    antiguedad_laboral = np.clip(antiguedad_laboral, 0.5, 35.0)
    
    # Ingresos y montos
    ingreso_mensual = np.random.lognormal(mean=6.5, sigma=0.5, size=n).round(2) # median ~ 665 USD
    ingreso_mensual = np.clip(ingreso_mensual, 350.0, 4500.0)
    
    plazo_meses = np.random.choice([6, 12, 18, 24, 36, 48, 60], size=n, p=[0.10, 0.25, 0.20, 0.25, 0.10, 0.06, 0.04])
    monto_credito = (ingreso_mensual * np.random.uniform(1.5, 8.0, size=n)).round(2)
    monto_credito = np.clip(monto_credito, 500.0, 15000.0)
    
    # Cuota mensual basada en tasa anual simulada (~18% anual)
    tasa_mensual = 0.18 / 12
    cuota_mensual = (monto_credito * (tasa_mensual * (1 + tasa_mensual)**plazo_meses) / ((1 + tasa_mensual)**plazo_meses - 1)).round(2)
    
    score_credito_buro = np.random.normal(loc=650, scale=85, size=n).astype(int)
    score_credito_buro = np.clip(score_credito_buro, 300, 850)
    
    num_creditos_previos = np.random.poisson(lam=2.2, size=n)
    creditos_previos_pagados_ok = [np.random.randint(0, num_creditos_previos[i] + 1) if num_creditos_previos[i] > 0 else 0 for i in range(n)]
    creditos_previos_pagados_ok = np.array(creditos_previos_pagados_ok)
    
    mora_maxima_historica = np.random.choice(['Sin_Mora', '1_30_dias', '31_60_dias', '61_90_dias'], size=n, p=[0.65, 0.20, 0.10, 0.05])
    posee_garantia = np.random.choice(['Si', 'No'], size=n, p=[0.42, 0.58])
    valor_garantia = [round(monto_credito[i] * np.random.uniform(0.8, 1.8), 2) if posee_garantia[i] == 'Si' else 0.0 for i in range(n)]
    valor_garantia = np.array(valor_garantia)
    
    gastos_familiares_mensuales = (ingreso_mensual * np.random.uniform(0.35, 0.70, size=n)).round(2)
    tarjeta_credito_activa = np.random.choice(['Si', 'No'], size=n, p=[0.45, 0.55])
    
    # Logit para default
    ratio_cuota_ingreso = cuota_mensual / ingreso_mensual
    score_norm = (score_credito_buro - 300) / 550.0
    
    mora_factor = np.where(mora_maxima_historica == 'Sin_Mora', -0.8,
                  np.where(mora_maxima_historica == '1_30_dias', 0.2,
                  np.where(mora_maxima_historica == '31_60_dias', 1.1, 2.0)))
    
    trabajo_factor = np.where(tipo_trabajo == 'Informal', 0.9,
                     np.where(tipo_trabajo == 'Independiente', 0.4,
                     np.where(tipo_trabajo == 'Dependiente_Privado', 0.0, -0.5)))
    
    garantia_factor = np.where(posee_garantia == 'No', 0.5, -0.4)
    
    logit = (-0.4 
             + 3.5 * ratio_cuota_ingreso 
             - 3.2 * score_norm 
             + mora_factor 
             + trabajo_factor 
             + garantia_factor 
             - 0.08 * antiguedad_laboral
             + np.random.normal(0, 0.75, size=n))
             
    prob_default = 1 / (1 + np.exp(-logit))
    default = (prob_default > 0.45).astype(int)
    
    df = pd.DataFrame({
        'id_cliente': id_cliente,
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
        'tarjeta_credito_activa': tarjeta_credito_activa,
        'default': default
    })
    
    # Inyectar ~0.2% de nulos en 'gastos_familiares_mensuales' (15 nulos)
    null_idx = np.random.choice(df.index, size=15, replace=False)
    df.loc[null_idx, 'gastos_familiares_mensuales'] = np.nan
    
    # Inyectar 25 filas duplicadas idénticas
    dup_idx = np.random.choice(df.index, size=25, replace=False)
    df_dups = df.loc[dup_idx].copy()
    df = pd.concat([df, df_dups], ignore_index=True)
    
    output_path = os.path.join('data', 'credit_risk_dataset.csv')
    df.to_csv(output_path, index=False)
    print(f"Dataset generado exitosamente en {output_path} con {len(df)} registros y {len(df.columns)} columnas.")
    print(f"Tasa global de default: {df['default'].mean()*100:.2f}%")

if __name__ == '__main__':
    generate_credit_dataset()
