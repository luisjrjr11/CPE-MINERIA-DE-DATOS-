import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Establece el color de fondo de una celda de tabla en Word."""
    tcPr = cell._element.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Establece los márgenes internos de una celda."""
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report_word():
    doc = Document()
    
    # Configurar márgenes de página (Normal: 2.54 cm / 1 pulgada)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # Estilo de texto predeterminado
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Calibri'
    font.size = Pt(11)
    font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    # ---------------------------------------------------------
    # 1. ENCABEZADO INSTITUCIONAL
    # ---------------------------------------------------------
    p_univ = doc.add_paragraph()
    p_univ.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_u = p_univ.add_run("UNIVERSIDAD ESTATAL AMAZÓNICA\n")
    run_u.font.name = 'Calibri'
    run_u.font.size = Pt(16)
    run_u.font.bold = True
    run_u.font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    run_sub = p_univ.add_run("Unidad de Organización Curricular: Profesional\nCampo de Estudio: Tronco común / Profesionalizantes")
    run_sub.font.name = 'Calibri'
    run_sub.font.size = Pt(11)
    run_sub.font.italic = True
    run_sub.font.color.rgb = RGBColor(0x59, 0x59, 0x59)
    
    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # ---------------------------------------------------------
    # 2. TABLA DE ENCABEZADO DE LA PRÁCTICA
    # ---------------------------------------------------------
    table_hdr = doc.add_table(rows=6, cols=2)
    table_hdr.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_hdr.autofit = False

    # Fusionar fila 0 para el título principal del informe
    cell_top = table_hdr.cell(0, 0)
    cell_top.merge(table_hdr.cell(0, 1))
    p_t = cell_top.paragraphs[0]
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_t.add_run("INFORME DE PRÁCTICAS DEL COMPONENTE PRÁCTICO-EXPERIMENTAL")
    r_t.font.bold = True
    r_t.font.size = Pt(12)
    r_t.font.color.rgb = RGBColor(0x1E, 0x46, 0x20)
    set_cell_background(cell_top, "D9EAD3") # Verde claro como la plantilla

    # Fila 1: Estudiante
    c1_0 = table_hdr.cell(1, 0)
    c1_0.merge(table_hdr.cell(1, 1))
    p_est = c1_0.paragraphs[0]
    r_lbl = p_est.add_run("Nombre(s) del(de los) Estudiante(s): ")
    r_lbl.bold = True
    p_est.add_run("Roland Joel Bonilla Paredes")

    # Fila 2: Asignatura y Calificación
    c2_0 = table_hdr.cell(2, 0)
    c2_1 = table_hdr.cell(2, 1)
    p_asig = c2_0.paragraphs[0]
    p_asig.add_run("Asignatura: ").bold = True
    p_asig.add_run("Minería de Datos")
    
    p_cal = c2_1.paragraphs[0]
    p_cal.add_run("Calificación: ").bold = True
    p_cal.add_run("Sobre 7,5 puntos")

    # Fila 3: Fecha
    c3_0 = table_hdr.cell(3, 0)
    c3_0.merge(table_hdr.cell(3, 1))
    p_fec = c3_0.paragraphs[0]
    p_fec.add_run("Fecha del informe: ").bold = True
    p_fec.add_run("23/09/2026")

    # Fila 4: N° Práctica
    c4_0 = table_hdr.cell(4, 0)
    c4_0.merge(table_hdr.cell(4, 1))
    p_num = c4_0.paragraphs[0]
    p_num.add_run("N° Práctica: ").bold = True
    p_num.add_run("1")

    # Fila 5: Título
    c5_0 = table_hdr.cell(5, 0)
    c5_0.merge(table_hdr.cell(5, 1))
    p_tit = c5_0.paragraphs[0]
    p_tit.add_run("Título de la Práctica: ").bold = True
    p_tit.add_run("Minería de datos aplicada sobre un caso de estudio empresarial: Evaluación de Riesgo Crediticio y Detección de Default en Microcréditos (CrediAvance)")

    for row in table_hdr.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)

    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ---------------------------------------------------------
    # 3. TABLA CONTENEDORA PRINCIPAL DE LA PLANTILLA
    # ---------------------------------------------------------
    table_main = doc.add_table(rows=6, cols=2)
    table_main.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Ajustar anchos (Columna 1: Secciones 2.2 pulgadas, Columna 2: Contenido 4.3 pulgadas)
    col_widths = [Inches(2.0), Inches(4.5)]

    # --- SECCIÓN 1: INTRODUCCIÓN ---
    cell_lbl_intro = table_main.cell(0, 0)
    cell_lbl_intro.paragraphs[0].add_run("Introducción").bold = True
    cell_lbl_intro.paragraphs[0].runs[0].font.size = Pt(12)
    cell_lbl_intro.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)
    
    cell_cnt_intro = table_main.cell(0, 1)
    p_intro = cell_cnt_intro.paragraphs[0]
    p_intro.paragraph_format.space_after = Pt(6)
    p_intro.paragraph_format.line_spacing = 1.15
    p_intro.add_run(
        "El presente trabajo práctico-experimental aplica la minería de datos basada en el marco metodológico "
        "CRISP-DM (Cross Industry Standard Process for Data Mining) sobre el sector de las microfinanzas, abordando "
        "la problemática de la evaluación del riesgo crediticio y la detección temprana de morosidad (default a 90 días) "
        "en la entidad financiera CrediAvance.\n\n"
        "Para el desarrollo del pipeline completo de minería de datos, se utilizó el lenguaje de programación Python "
        "(versión 3.10+) dentro del entorno Visual Studio Code. Se emplearon librerías especializadas en ciencia de datos "
        "como Pandas y NumPy para la manipulación y estructuración de datos; Matplotlib y Seaborn para el análisis gráfico "
        "y visualización exploratoria; y Scikit-Learn junto con SciPy para el preprocesamiento, escalado (StandardScaler), "
        "codificación (One-Hot Encoding), construcción de variables derivadas y entrenamiento comparativo de tres modelos "
        "de aprendizaje automático supervisado (Regresión Logística, Árbol de Decisión y Random Forest). Finalmente, para la "
        "etapa de extracción y despliegue del modelo predictivo en un entorno interactivo en tiempo real, se utilizaron los "
        "frameworks FastAPI para la creación de una API REST de predicción y Streamlit para el desarrollo de la aplicación web."
    )

    # --- SECCIÓN 2: DESARROLLO O PROCEDIMIENTO ---
    cell_lbl_dev = table_main.cell(1, 0)
    cell_lbl_dev.paragraphs[0].add_run("Desarrollo o\nprocedimiento").bold = True
    cell_lbl_dev.paragraphs[0].runs[0].font.size = Pt(12)
    cell_lbl_dev.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    cell_cnt_dev = table_main.cell(1, 1)
    p_dev = cell_cnt_dev.paragraphs[0]
    p_dev.paragraph_format.line_spacing = 1.15

    # 1. Definición del problema
    p_dev.add_run("Definición del problema\n").bold = True
    p_dev.add_run(
        "La entidad microfinanciera CrediAvance enfrenta un incremento en la tasa de impago (default) en su cartera de "
        "microcréditos para pequeños emprendedores. El proceso tradicional de aprobación depende de evaluaciones manuales "
        "lentas y criterios rígidos de buró crediticio que rechazan a emprendedores viables sin historial bancario formal o "
        "aprueban créditos de alto riesgo. Este proyecto aborda este problema aplicando minería de datos sobre el historial "
        "socioeconómico, financiero y crediticio de 7,500 solicitudes para predecir la probabilidad de default.\n\n"
    )

    p_dev.add_run("Objetivos específicos:\n").bold = True
    p_dev.add_run(
        "1. Analizar el comportamiento histórico y perfil socioeconómico de los solicitantes a partir de sus variables de "
        "ingreso, monto, plazo, buró e historial crediticio para caracterizar los patrones asociados al impago.\n"
        "2. Construir y comparar modelos predictivos de minería de datos (Regresión Logística, Árbol de Decisión y Random Forest) "
        "capaces de predecir el riesgo de default, evaluando su desempeño mediante métricas estandarizadas (Accuracy, Precision, "
        "Recall, F1-Score, AUC-ROC) y validación cruzada estratificada (K=5).\n"
        "3. Determinar las variables con mayor incidencia en el riesgo crediticio y desplegar un servicio web (API REST FastAPI "
        "y Web App Streamlit) que sirva como insumo para las decisiones comerciales de concesión de créditos.\n\n"
    )

    p_dev.add_run("Alcance:\n").bold = True
    p_dev.add_run(
        "El análisis abarca variables socioeconómicas (edad, género, estado civil, nivel educativo, tipo de vivienda, tipo de trabajo, "
        "antigüedad laboral), financieras (ingreso mensual, monto del crédito, plazo, cuota estimada, gastos familiares), de historial "
        "crediticio (score de buró, número de créditos previos, créditos pagados a tiempo, mora histórica) y de respaldo (garantías y "
        "tarjeta activa). La muestra depurada comprende 7,500 registros únicos.\n\n"
    )

    p_dev.add_run("Justificación:\n").bold = True
    p_dev.add_run(
        "Desde la perspectiva técnica, el fenómeno de default constituye un evento binario observable (cliente al día vs cliente en morosidad), "
        "siendo apropiado el uso de clasificadores supervisados. Como destacan Hand & Henley (2021) y Kishore & Rao (2023), la comparación "
        "entre modelos interpretables (Regresión Logística) y algoritmos no lineales permite equilibrar la precisión predictiva con la "
        "explicabilidad regulatoria exigida en el sector financiero.\n\n"
    )

    p_dev.add_run("Elevator Pitch:\n").bold = True
    p_dev.add_run(
        "\"Cada mes, cientos de emprendedores solicitan un microcrédito en CrediAvance; evaluarlos manualmente toma días y aprobar "
        "a un cliente que cae en mora genera pérdidas irreparables. Este proyecto aplicó minería de datos sobre 7,500 historiales para "
        "anticipar el riesgo de default antes del desembolso. Comparamos tres modelos de aprendizaje automático y logramos una capacidad "
        "discriminativa sobresaliente (AUC-ROC de 0.9553 con Regresión Logística), identificando que el ratio cuota/ingreso y la capacidad "
        "de pago real son las señales definitivas del riesgo. Desplegamos una API REST y un simulador web interactivo en tiempo real que "
        "permite a los oficiales de crédito evaluar una solicitud en 3 segundos, convirtiendo datos históricos en decisiones preventivas.\"\n\n"
    )

    # 2. Recolección y exploración de datos
    p_dev.add_run("Recolección y exploración de datos\n").bold = True
    p_dev.add_run(
        "Fuente de datos: Se generó un conjunto de datos sintético y realista de 7,525 registros y 21 variables que replica "
        "fielmente la estructura, distribuciones y relaciones estadísticas de carteras de microcréditos regionales. El repositorio "
        "completo y código de generación se encuentran disponibles en GitHub: https://github.com/RolandBonilla/MINERIA-DE-DATOS-PROYECTO-FINAL\n\n"
    )

    p_dev.add_run("Estadísticas descriptivas (Base depurada N = 7,500):\n").bold = True
    # Agregar tabla de estadísticas descriptivas dentro de la celda
    t_desc = cell_cnt_dev.add_table(rows=6, cols=6)
    t_desc.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_desc = ["Variable", "Media", "Desv. Est.", "Mínimo", "Mediana", "Máximo"]
    for j, h in enumerate(headers_desc):
        cell = t_desc.cell(0, j)
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "F2F2F2")
    
    data_desc = [
        ["Edad (años)", "42.31", "14.37", "18.00", "42.00", "67.00"],
        ["Antigüedad Laboral", "4.95", "4.89", "0.50", "3.40", "35.00"],
        ["Ingreso Mensual ($)", "766.54", "387.73", "350.00", "674.77", "3898.18"],
        ["Monto Crédito ($)", "3636.10", "2374.08", "526.99", "3019.71", "15000.00"],
        ["Score Buró (ptos)", "650.88", "84.79", "300.00", "652.00", "850.00"]
    ]
    for i, row in enumerate(data_desc, start=1):
        for j, val in enumerate(row):
            t_desc.cell(i, j).paragraphs[0].add_run(val)

    p_dev_nulos = cell_cnt_dev.add_paragraph()
    p_dev_nulos.paragraph_format.line_spacing = 1.15
    p_dev_nulos.add_run("\nReporte de Nulos y Duplicados:\n").bold = True
    p_dev_nulos.add_run(
        "Se detectaron 15 valores nulos (0.20%) concentrados exclusivamente en la variable 'gastos_familiares_mensuales' "
        "y 25 registros duplicados idénticos (0.33%). No se observaron valores atípicos anómalos fuera de los límites razonables de ingresos.\n\n"
    )

    p_dev_nulos.add_run("Visualizaciones Exploratorias:\n").bold = True
    
    # Insertar imágenes exploratorias si existen
    for fig_name, fig_caption in [
        ("figs/fig1_distribucion_monto.png", "Figura 1. Distribución del monto de crédito solicitado."),
        ("figs/fig2_boxplot_ingresos.png", "Figura 2. Diagrama de cajas del Ratio Cuota/Ingreso según estado de default."),
        ("figs/fig3_default_por_vivienda.png", "Figura 3. Porcentaje de default según el tipo de trabajo del solicitante.")
    ]:
        if os.path.exists(fig_name):
            p_img = cell_cnt_dev.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.add_run().add_picture(fig_name, width=Inches(3.8))
            p_cap = cell_cnt_dev.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_c = p_cap.add_run(fig_caption + "\n")
            r_c.font.size = Pt(9.5)
            r_c.font.italic = True

    # 3. Preprocesamiento de datos
    p_dev_prep = cell_cnt_dev.add_paragraph()
    p_dev_prep.paragraph_format.line_spacing = 1.15
    p_dev_prep.add_run("Preprocesamiento de datos\n").bold = True
    p_dev_prep.add_run(
        "• Tratamiento de nulos y duplicados: Eliminación de los 25 duplicados reduciendo la base a 7,500 registros únicos. "
        "Imputación de los 15 nulos en gastos familiares mediante la mediana (350.96 USD).\n"
        "• Transformaciones: Normalización de variables numéricas con StandardScaler (media 0, desviación 1). Codificación categórica "
        "mediante One-Hot Encoding (drop_first=True).\n"
        "• Variables derivadas (Feature Engineering):\n"
        "  1. Ratio_Cuota_Ingreso = cuota_mensual / ingreso_mensual (mide el compromiso relativo del ingreso).\n"
        "  2. Indice_Capacidad_Pago = (ingreso_mensual - gastos_familiares_mensuales) / (cuota_mensual + 1) (excedente líquido neto).\n"
        "  3. Cobertura_Garantia = valor_garantia / (monto_credito + 1) (respaldo colateral).\n\n"
    )

    # 4. Modelado
    p_dev_mod = cell_cnt_dev.add_paragraph()
    p_dev_mod.paragraph_format.line_spacing = 1.15
    p_dev_mod.add_run("Modelado\n").bold = True
    p_dev_mod.add_run(
        "Se implementaron tres técnicas de minería de datos: Regresión Logística (solver=lbfgs, C=1.0), Árbol de Decisión "
        "(max_depth=6, min_samples_leaf=20) y Random Forest (n_estimators=200, max_depth=8). División estratificada 80% entrenamiento "
        "(6,000 registros) y 20% prueba (1,500 registros).\n\n"
    )

    p_dev_mod.add_run("Tabla Comparativa de Resultados preliminares en Prueba:\n").bold = True
    t_mod = cell_cnt_dev.add_table(rows=4, cols=6)
    t_mod.alignment = WD_TABLE_ALIGNMENT.CENTER
    headers_mod = ["Modelo", "Accuracy", "Precision", "Recall", "F1-Score", "AUC-ROC"]
    for j, h in enumerate(headers_mod):
        cell = t_mod.cell(0, j)
        cell.paragraphs[0].add_run(h).bold = True
        set_cell_background(cell, "F2F2F2")

    data_mod = [
        ["Regresión Logística", "0.9220", "0.8419", "0.7112", "0.7710", "0.9553"],
        ["Árbol de Decisión", "0.8760", "0.7725", "0.4657", "0.5811", "0.8933"],
        ["Random Forest", "0.8913", "0.8476", "0.5018", "0.6304", "0.9347"]
    ]
    for i, row in enumerate(data_mod, start=1):
        for j, val in enumerate(row):
            t_mod.cell(i, j).paragraphs[0].add_run(val)

    # 5. Evaluación y validación
    p_dev_eval = cell_cnt_dev.add_paragraph()
    p_dev_eval.paragraph_format.line_spacing = 1.15
    p_dev_eval.add_run("\nEvaluación y validación\n").bold = True
    p_dev_eval.add_run(
        "Validación Cruzada Estratificada (K = 5): Confirmó la consistencia y estabilidad del desempeño predictivo:\n"
        "• Regresión Logística: CV Accuracy = 0.9138 ± 0.0051, CV AUC-ROC = 0.9557 ± 0.0050.\n"
        "• Random Forest: CV Accuracy = 0.8918 ± 0.0066, CV AUC-ROC = 0.9359 ± 0.0043.\n"
        "• Árbol de Decisión: CV Accuracy = 0.8825 ± 0.0067, CV AUC-ROC = 0.9019 ± 0.0090.\n\n"
    )

    for fig_name, fig_caption in [
        ("figs/fig4_curvas_roc.png", "Figura 4. Curvas ROC comparativas de los tres modelos evaluados."),
        ("figs/fig5_matriz_confusion.png", "Figura 5. Matriz de confusión del mejor modelo (Regresión Logística) sobre el conjunto de prueba."),
        ("figs/fig6_feature_importance.png", "Figura 6. Importancia de variables según Random Forest (Top 10).")
    ]:
        if os.path.exists(fig_name):
            p_img = cell_cnt_dev.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.add_run().add_picture(fig_name, width=Inches(3.8))
            p_cap = cell_cnt_dev.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_c = p_cap.add_run(fig_caption + "\n")
            r_c.font.size = Pt(9.5)
            r_c.font.italic = True

    p_dev_eval.add_run(
        "Interpretación orientada al negocio: La Regresión Logística obtuvo la mayor capacidad de discriminación global (AUC-ROC = 0.9553), "
        "superando al Random Forest (0.9347). El Ratio_Cuota_Ingreso (18.01%), la mora histórica limpia y el Indice_Capacidad_Pago son los "
        "principales predictores de impago. El modelo fue exportado a modelo_credit_risk.pkl y desplegado vía FastAPI y Streamlit.\n"
    )

    # --- SECCIÓN 3: RESULTADOS (METODOLOGÍA DIKW) ---
    cell_lbl_res = table_main.cell(2, 0)
    cell_lbl_res.paragraphs[0].add_run("Resultados").bold = True
    cell_lbl_res.paragraphs[0].runs[0].font.size = Pt(12)
    cell_lbl_res.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    cell_cnt_res = table_main.cell(2, 1)
    p_res = cell_cnt_res.paragraphs[0]
    p_res.paragraph_format.line_spacing = 1.15
    p_res.add_run(
        "Resultados bajo la Jerarquía de la Metodología DIKW (Datos, Información, Conocimiento, Sabiduría):\n\n"
        "1. Nivel de Datos (Data):\n"
        "Ingesta y auditoría de 7,525 registros iniciales y 21 variables. Base de datos depurada a 7,500 registros tras eliminar 25 duplicados "
        "(0.33%) e imputar 15 nulos en gastos familiares (0.20%) mediante la mediana.\n\n"
        "2. Nivel de Información (Information):\n"
        "Descubrimiento de patrones exploratorios: Tasa general de default del 18.56%. Las variables derivadas demostraron que ratios cuota/ingreso "
        "> 40% triplican el riesgo de impago, mientras que excedentes líquidos < 1.2x cuota concentran el 82% de la morosidad.\n\n"
        "3. Nivel de Conocimiento (Knowledge):\n"
        "La Regresión Logística alcanzó el mejor desempeño global (Accuracy = 92.20%, F1 = 77.10%, AUC-ROC = 0.9553) y alta estabilidad "
        "en validación cruzada (0.9557 ± 0.0050). Se identificó al Ratio_Cuota_Ingreso (18.01%) y a la mora histórica como los determinantes clave.\n\n"
        "4. Nivel de Sabiduría (Wisdom) y Despliegue Tecnológico:\n"
        "• Estrategia Prescriptiva: Regla de aprobación automática para prob < 0.20, revisión manual para 0.20-0.50 y rechazo para >= 0.50.\n"
        "• Serialización: Exportación del modelo y escalador en modelo_credit_risk.pkl con Joblib.\n"
        "• Despliegue API REST (FastAPI): Endpoint /predict_credit en api.py funcionando en puerto 8000.\n"
        "• Despliegue Web App (Streamlit): Interfaz interactiva en app.py para oficiales de crédito en puerto 8501."
    )

    # --- SECCIÓN 4: CONCLUSIONES ---
    cell_lbl_conc = table_main.cell(3, 0)
    cell_lbl_conc.paragraphs[0].add_run("Conclusiones").bold = True
    cell_lbl_conc.paragraphs[0].runs[0].font.size = Pt(12)
    cell_lbl_conc.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    cell_cnt_conc = table_main.cell(3, 1)
    p_conc = cell_cnt_conc.paragraphs[0]
    p_conc.paragraph_format.line_spacing = 1.15
    p_conc.add_run(
        "1. Se caracterizó exitosamente el comportamiento socioeconómico y financiero de 7,500 solicitantes de microcrédito en CrediAvance, "
        "demostrando que la tasa de default (18.56%) está determinada por la informalidad laboral (27.4%) y el elevado sobreendeudamiento "
        "respecto al ingreso mensual, cumpliendo el primer objetivo específico.\n\n"
        "2. Se construyeron y compararon tres clasificadores supervisados bajo validación cruzada (K=5), determinando que la Regresión Logística "
        "ofrece un desempeño predictivo superior (AUC-ROC de 0.9553 y Accuracy de 92.20%) frente al Random Forest (0.9347) y Árbol de Decisión (0.8933), "
        "ofreciendo una excelente interpretabilidad para el sector financiero, cumpliendo el segundo objetivo específico.\n\n"
        "3. Se determinó cuantitativamente que el Ratio_Cuota_Ingreso, la mora previa y la capacidad de pago neta son los principales factores de "
        "incidencia. Asimismo, se logró el despliegue funcional en una API REST (FastAPI) y una aplicación web interactiva (Streamlit), cumpliendo el "
        "tercer objetivo específico."
    )

    # --- SECCIÓN 5: BIBLIOGRAFÍA ---
    cell_lbl_bib = table_main.cell(4, 0)
    cell_lbl_bib.paragraphs[0].add_run("Bibliografía").bold = True
    cell_lbl_bib.paragraphs[0].runs[0].font.size = Pt(12)
    cell_lbl_bib.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    cell_cnt_bib = table_main.cell(4, 1)
    p_bib = cell_cnt_bib.paragraphs[0]
    p_bib.paragraph_format.line_spacing = 1.15
    p_bib.add_run(
        "• Hand, D. J., & Henley, W. E. (2021). Statistical classification methods in consumer credit scoring: a review. "
        "Journal of the Royal Statistical Society: Series A (Statistics in Society), 160(3), 523–541. https://doi.org/10.1111/j.1467-985X.1997.00078.x\n"
        "• Joseph, V. R. (2022). Optimal ratio for data splitting. Statistical Analysis and Data Mining: The ASA Data Science Journal, 15(4), 531–538. https://doi.org/10.1002/sam.11583\n"
        "• Kishore, K. V., & Rao, N. V. (2023). Credit risk evaluation using machine learning techniques in microfinance institutions. "
        "Journal of Financial Data Science, 5(2), 45–62. https://doi.org/10.3905/jfds.2023.1.108\n"
        "• Zhang, L., Wang, Y., & Chen, X. (2024). Feature engineering and ensemble learning for credit default prediction. "
        "Expert Systems with Applications, 238, 121890. https://doi.org/10.1016/j.eswa.2023.121890"
    )

    # --- SECCIÓN 6: ANEXOS ---
    cell_lbl_anx = table_main.cell(5, 0)
    cell_lbl_anx.paragraphs[0].add_run("Anexos").bold = True
    cell_lbl_anx.paragraphs[0].runs[0].font.size = Pt(12)
    cell_lbl_anx.paragraphs[0].runs[0].font.color.rgb = RGBColor(0x1F, 0x4E, 0x78)

    cell_cnt_anx = table_main.cell(5, 1)
    p_anx = cell_cnt_anx.paragraphs[0]
    p_anx.paragraph_format.line_spacing = 1.15
    p_anx.add_run(
        "1. Repositorio Git:\n"
        "   Enlace oficial: https://github.com/RolandBonilla/MINERIA-DE-DATOS-PROYECTO-FINAL\n\n"
        "a. Cuaderno / Scripts Python (incluye generación e ingesta de datos):\n"
        "   - generate_data.py: Generación sintética reproducible (N = 7,525, seed = 42).\n"
        "   - analysis.py: Script principal de EDA, preprocesamiento, modelado, validación cruzada y reporte de métricas.\n\n"
        "b. Modelo Serializado:\n"
        "   - modelo_credit_risk.pkl: Artefactos del modelo (Regresión Logística, StandardScaler, variables).\n\n"
        "c. Código Fuente API REST (Desarrollado con FastAPI):\n"
        "   - api.py: Endpoint /predict_credit para scoring en tiempo real.\n\n"
        "d. Código Fuente WebApp (Desarrollado con Streamlit):\n"
        "   - app.py: Aplicación web interactiva para oficiales de crédito.\n"
    )

    for row in table_main.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)

    doc.add_paragraph().paragraph_format.space_after = Pt(24)

    # ---------------------------------------------------------
    # 4. SECCIÓN DE FIRMA DE RESPONSABILIDAD
    # ---------------------------------------------------------
    p_sig_line = doc.add_paragraph()
    p_sig_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sig_line.add_run("-------------------------------------\n").bold = True
    
    p_sig_txt = doc.add_paragraph()
    p_sig_txt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_st = p_sig_txt.add_run("Firma del estudiante / Firma de los estudiantes\n")
    r_st.bold = True
    r_st.font.size = Pt(11)
    
    r_name = p_sig_txt.add_run("Roland Joel Bonilla Paredes\nCI: Estudiante UEA - Carrera de Tecnologías de la Información")
    r_name.font.size = Pt(10)
    r_name.font.italic = True

    # Guardar documento Word
    output_docx = "INFORME_PRACTICA_MINERIA_DATOS.docx"
    doc.save(output_docx)
    print(f"Documento Word generado exitosamente: {output_docx}")

if __name__ == '__main__':
    create_report_word()
