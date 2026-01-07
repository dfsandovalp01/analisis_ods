"""
APLICACIÓN WEB GRADIO - VISUALIZACIONES ODS
============================================

Aplicación interactiva que permite explorar las 10 visualizaciones
de análisis de similaridad ODS a través de una interfaz web amigable.

Características:
- Interfaz con pestañas para cada visualización
- Explicaciones integradas para público general
- Visualizaciones interactivas (HTML) y estáticas (PNG)
- Estadísticas en tiempo real
- Diseño responsivo y profesional

Autor: Daniel Sandvoval
Fecha: Noviembre 2025
"""

import gradio as gr
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import seaborn as sns
from src.embeddings.modelos_nlp_db import search

# Importar funciones de visualización
import sys
# sys.path.insert(0, '/home/claude')
from src.visualization.visualizaciones_ods import (
    cargar_datos,
    viz_1_distribucion_por_ods,
    viz_2_heatmap_ods_ranking,
    viz_3_scatter_3d_interactivo,
    viz_4_radar_chart_ods,
    viz_5_sunburst_jerarquia,
    viz_6_top_indicadores_por_ods,
    viz_7_streamgraph_similaridad,
    viz_8_violin_plot_ods,
    viz_9_dashboard_metricas,
    viz_10_matriz_transicion,
    analisis_estadistico
)

# ============================================================================
# CONFIGURACIÓN GLOBAL
# ============================================================================
import os
import base64

levels = ['ODS_ID','META_ID','INDICADOR_ID']


def convertir_logo_a_base64(logo_path):
    """Convierte un logo a base64 para incrustar en HTML"""
    # try:
    #     rutas_posibles = [
    #         logo_path,
    #         os.path.join(os.path.dirname(__file__), logo_path),
    #         os.path.join('/mnt/user-data/outputs', logo_path),
    #     ]
        
    #     for ruta in rutas_posibles:
    #         if os.path.exists(ruta):
    #             with open(ruta, "rb") as image_file:
    #                 encoded = base64.b64encode(image_file.read()).decode()
    #                 return f"data:image/png;base64,{encoded}"
        
    #     print(f"⚠️  Logo no encontrado: {logo_path}")
    #     return ""
    # except Exception as e:
    #     print(f"⚠️  Error al cargar logo: {e}")
    #     return ""
    ruta = Path('config/institucional/logos')
    with open(Path(f'{ruta}/{logo_path}'), "rb") as image_file:
      encoded = base64.b64encode(image_file.read()).decode()
      return f"data:image/png;base64,{encoded}"



# Cargar logos una sola vez al iniciar
print("Cargando logos institucionales...")
LOGO_GOBIERNO = convertir_logo_a_base64("/institucional/GOBIERNO-DE-COLOMBIA_HORIZONTAL.webp")
LOGO_FONDO = convertir_logo_a_base64("/institucional/LOGO MPTF (ESP).webp")


if LOGO_GOBIERNO and LOGO_FONDO:
    print("✅ Logos cargados correctamente")
else:
    print("⚠️  Algunos logos no se pudieron cargar")

dict_logos = {
  'gobierno': convertir_logo_a_base64("/institucional/GOBIERNO-DE-COLOMBIA_HORIZONTAL.webp"),
  'fondo_un': convertir_logo_a_base64("/institucional/LOGO MPTF (ESP).webp"),
  'ods_1': convertir_logo_a_base64("/ods/S-WEB-Goal-01.webp"),
  'ods_2': convertir_logo_a_base64("/ods/S-WEB-Goal-02.webp"),
  'ods_3': convertir_logo_a_base64("/ods/S-WEB-Goal-03.webp"),
  'ods_4': convertir_logo_a_base64("/ods/S-WEB-Goal-04.webp"),
  'ods_5': convertir_logo_a_base64("/ods/S-WEB-Goal-05.webp"),
  'ods_6': convertir_logo_a_base64("/ods/S-WEB-Goal-06.webp"),
  'ods_7': convertir_logo_a_base64("/ods/S-WEB-Goal-07.webp"),
  'ods_8': convertir_logo_a_base64("/ods/S-WEB-Goal-08.webp"),
  'ods_9': convertir_logo_a_base64("/ods/S-WEB-Goal-09.webp"),
  'ods_10': convertir_logo_a_base64("/ods/S-WEB-Goal-10.webp"),
  'ods_11': convertir_logo_a_base64("/ods/S-WEB-Goal-11.webp"),
  'ods_12': convertir_logo_a_base64("/ods/S-WEB-Goal-12.webp"),
  'ods_13': convertir_logo_a_base64("/ods/S-WEB-Goal-13.webp"),
  'ods_14': convertir_logo_a_base64("/ods/S-WEB-Goal-14.webp"),
  'ods_15': convertir_logo_a_base64("/ods/S-WEB-Goal-15.webp"),
  'ods_16': convertir_logo_a_base64("/ods/S-WEB-Goal-16.webp"),
  'ods_17': convertir_logo_a_base64("/ods/S-WEB-Goal-17.webp"),  
}

# Ruta al archivo de datos
# # RUTA_DATOS = '/mnt/user-data/uploads/indicadores_markdown.txt'
# RUTA_DATOS = '/content/drive/MyDrive/Compartida/06_Desarrollo de la herramienta IA/01_MPTF /archivos_trabajo/app_visualizaciones/indicadores_markdown.txt'

# # Cargar datos globalmente para toda la app
# try:
#     df_global = cargar_datos(RUTA_DATOS)
DATOS_CARGADOS = True
#     print(f"✓ Datos cargados: {len(df_global)} registros")
# except Exception as e:
#     df_global = None
#     DATOS_CARGADOS = False
#     print(f"✗ Error al cargar datos: {e}")



# Estilos CSS personalizados
CUSTOM_CSS = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.explanation-box {
    background-color: #E8F4F8;
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid #2E5090;
    margin: 10px 0;
}
.stats-box {
    background-color: #FFF9E6;
    padding: 15px;
    border-radius: 8px;
    border: 2px solid #FFD700;
    margin: 10px 0;
}
.important-box {
    background-color: #FFE6E6;
    padding: 15px;
    border-radius: 8px;
    border-left: 5px solid #C00000;
    margin: 10px 0;
}
h1, h2, h3 {
    color: #2E5090;
}
.tab-nav button {
    font-size: 16px;
    padding: 10px 20px;
}

/* ESTILOS PARA HEADER CON LOGOS INSTITUCIONALES */
.header-institucional {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 40px;
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 50%, #f8f9fa 100%);
    border-bottom: 4px solid #003DA5;
    margin-bottom: 25px;
    box-shadow: 0 3px 10px rgba(0,0,0,0.08);
}

.logo-institucional {
    height: 40px;
    width: auto;
    object-fit: contain;
}

.titulo-institucional {
    flex: 1;
    text-align: center;
    padding: 0 30px;
}

.titulo-institucional h1 {
    margin: 0;
    color: #003DA5 !important;
    font-size: 28px;
    font-weight: 700;
}

.logo-ods-tbl {
    height: 60px;
    width: auto;
    object-fit: contain;
}

@media (max-width: 768px) {
    .header-institucional {
        padding: 15px 20px;
        flex-direction: column;
        gap: 15px;
    }
    .logo-institucional {
        height: 50px;
    }
}
"""

# ============================================================================
# FUNCIONES DE CONVERSIÓN DE FIGURAS
# ============================================================================

def plotly_to_html(fig):
    """Convierte figura Plotly a HTML para mostrar en Gradio"""
    return fig.to_html(include_plotlyjs='cdn', full_html=False)

def matplotlib_to_file(fig, filename):
    """Convierte figura Matplotlib a archivo temporal"""
    import tempfile
    import os
    
    # Crear directorio temporal si no existe
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    
    # Guardar la figura
    fig.savefig(filepath, format='png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    
    return filepath

# ============================================================================
# FUNCIONES PARA CADA PESTAÑA
# ============================================================================

def tab_inicio(df_ods, df_metas, df_indicador):
# def tab_inicio():
    """Pestaña de inicio con resumen general"""
    if not DATOS_CARGADOS:
        return "⚠️ Error: No se pudieron cargar los datos."
    
    # Estadísticas básicas
    
    total_ods = df_ods['ODS_ID'].nunique()
    total_metas = df_metas['META_ID'].nunique()
    total_indicadores = df_indicador['INDICADOR_ID'].nunique()
    sim_media = df_ods['ods_similaridad_cos_normalized'].mean()
    sim_max = df_ods['ods_similaridad_cos_normalized'].max()
    sim_min = df_ods['ods_similaridad_cos_normalized'].min()
    correlacion = df_ods['ods_rank'].corr(df_ods['ods_similaridad_cos_normalized'])
    
    # Top 4 ODS
    top_ods = df_ods.nsmallest(4, 'ods_rank')[['ODS_ID','ods_rank','OBJETIVO','ods_similaridad_cos_normalized']]
    top_ods['logo_id'] = top_ods['ODS_ID'].apply(lambda _: f"ods_{_}") 
    # top_ods = df_ods.groupby('ODS_ID').agg({
    #     'ods_similaridad_cos_normalized': 'mean'
    # }).sort_values('ods_similaridad_cos_normalized', ascending=False).head(3)[['ods_similaridad_cos_normalized']]
    
    # Top ODS referencia
    ods_ref = top_ods.ODS_ID

    # Top 3 METAS
    
    top_metas = pd.DataFrame()
    for i in ods_ref:
      top_metas_lcl = df_metas[df_metas.ODS_ID == i]
      top_metas_lcl = top_metas_lcl.nsmallest(2, 'meta_rank')[['META_ID','meta_rank','META','meta_similaridad_cos_normalized', 'ODS_ID']]
      top_metas = pd.concat([top_metas, top_metas_lcl], axis=0)
    top_metas['logo_id'] = top_metas['ODS_ID'].apply(lambda _: f"ods_{_}")
    # top_metas = df_metas.groupby('META_ID').agg({
    #     'meta_similaridad_cos_normalized': 'mean'
    # }).sort_values('meta_similaridad_cos_normalized', ascending=False).head(5)[['META_ID','META','meta_similaridad_cos_normalized']]
    
    # Top 5 indicadores
    top_indicador = pd.DataFrame()
    for i in ods_ref:
      top_indicador_lcl = df_indicador[df_indicador.ODS_ID == i]
      top_indicador_lcl = top_indicador_lcl.nsmallest(2, 'indicador_rank')[['INDICADOR_ID', 'indicador_rank', 'INDICADOR', 'indicador_similaridad_cos_normalized', 'ODS_ID']]
      top_indicador = pd.concat([top_indicador, top_indicador_lcl], axis=0)
    top_indicador['logo_id'] = top_indicador['ODS_ID'].apply(lambda _: f"ods_{_}")
    
    
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h1 style="color: #2E5090; text-align: center;">
            📊 Sistema de Visualización ODS
        </h1>
        <h2 style="color: #4472C4; text-align: center;">
            Análisis de Similaridad de Indicadores
        </h2>
        
        <div class="stats-box" style="background-color: #E8F4F8; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: #2E5090;">📈 Estadísticas Generales</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Total de indicadores analizados:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{total_indicadores}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>ODS cubiertos:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{total_ods}/17 (100%)</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Similaridad promedio:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{sim_media:.4f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Rango de similaridad:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{sim_min:.4f} - {sim_max:.4f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Correlación Rank-Similaridad:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right; color: {'green' if correlacion < -0.7 else 'orange'};">
                        {correlacion:.4f} {'✅' if correlacion < -0.7 else '⚠️'}
                    </td>
                </tr>
            </table>
        </div>
        
        

        <div class="important-box" style="background-color: #E6F7E6; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #28A745;">
            <h3 style="color: #28A745;">🏆 Top 4 ODS Más Relevantes</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="background-color: #FFD700;">
                        <th style="padding: 10px; text-align: left;">Rank</th>
                        <th style="padding: 10px; text-align: left;"> </th>
                        <th style="padding: 10px; text-align: left;">ID</th>
                        <th style="padding: 10px; text-align: left;">ODS</th>
                        <!-- <th style="padding: 10px; text-align: center;">ODS</th> -->
                        <th style="padding: 10px; text-align: right;">Similaridad</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''<tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{row['ods_rank']}</td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><img src="{dict_logos[row['logo_id']]}" 
                                                                                    alt="ODS {row['ODS_ID']}" 
                                                                                    class="logo-ods-tbl"></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>{row['ODS_ID']}</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">{row['OBJETIVO']}</td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{row['ods_similaridad_cos_normalized']:.4f}</td>
                    </tr>''' for _, row in top_ods.iterrows()])}
                </tbody>
            </table>
        </div>

        <div class="important-box" style="background-color: #E6F7E6; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #FFD700;">
            <h3 style="color: #FF8C00;">🎯 Top 5 Metas Más Relevantes</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="background-color: #FFD700;">
                        <th style="padding: 10px; text-align: left;">Rank</th>
                        <th style="padding: 10px; text-align: left;"> </th>
                        <th style="padding: 10px; text-align: left;">ID </th>
                        <th style="padding: 10px; text-align: left;">Meta</th>
                        <!-- <th style="padding: 10px; text-align: center;">ODS</th> -->
                        <th style="padding: 10px; text-align: right;">Similaridad</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''<tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{row['meta_rank']}</td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><img src="{dict_logos[row['logo_id']]}" 
                                                                                    alt="ODS {row['ODS_ID']}" 
                                                                                    class="logo-ods-tbl"></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>{row['META_ID']}</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">{row['META']}</td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{row['meta_similaridad_cos_normalized']:.4f}</td>
                    </tr>''' for _, row in top_metas.iterrows()])}
                </tbody>
            </table>
        </div>
        
        <div class="important-box" style="background-color: #FFF9E6; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #FFD700;">
            <h3 style="color: #FF8C00;">🎯 Top 5 Indicadores Más Relevantes</h3>
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="background-color: #FFD700;">
                        <th style="padding: 10px; text-align: left;">Rank</th>
                        <th style="padding: 10px; text-align: left;"> </th>
                        <th style="padding: 10px; text-align: left;">ID </th>
                        <th style="padding: 10px; text-align: left;">Indicador</th>
                        <!-- <th style="padding: 10px; text-align: center;">ODS</th> -->
                        <th style="padding: 10px; text-align: right;">Similaridad</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''<tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;">{row['indicador_rank']}</td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><img src="{dict_logos[row['logo_id']]}" 
                                                                                    alt="ODS {row['ODS_ID']}" 
                                                                                    class="logo-ods-tbl"></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>{row['INDICADOR_ID']}</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: center;">{row['INDICADOR']}</td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{row['indicador_similaridad_cos_normalized']:.4f}</td>
                    </tr>''' for _, row in top_indicador.iterrows()])}
                </tbody>
            </table>
        </div>
        
        <div style="background-color: #F0F0F0; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="color: #2E5090;">📚 Cómo usar esta aplicación</h3>
            <ol style="line-height: 1.8;">
                <li><strong>Explora las pestañas:</strong> Cada pestaña contiene una visualización diferente</li>
                <li><strong>Lee las explicaciones:</strong> Cada gráfica incluye una guía de interpretación</li>
                <li><strong>Interactúa:</strong> Las visualizaciones HTML permiten zoom, hover y exploración</li>
                <li><strong>Descarga:</strong> Puedes descargar las imágenes desde las pestañas</li>
            </ol>
        </div>
        
        <div style="text-align: center; margin-top: 30px; padding: 20px; background-color: #E8F4F8; border-radius: 10px;">
            <p style="font-size: 18px; color: #2E5090;">
                <strong>¡Comienza explorando las visualizaciones en las pestañas superiores!</strong>
            </p>
            <p style="color: #666;">
                Recomendación: Empieza con el "Dashboard Integrado" para una vista general
            </p>
        </div>
    </div>
    """
    return html

def tab_viz1(df_ods, df_metas, df_indicador):
# def tab_viz1():
    """Visualización 1: Box Plot por ODS"""
    if not DATOS_CARGADOS:
        return None, "⚠️ Error: No se pudieron cargar los datos."
    
    fig1 = viz_1_distribucion_por_ods(df_ods, 'ODS_ID', 'ods_similaridad_cos_normalized', 'ODS')
    fig2 = viz_1_distribucion_por_ods(df_metas, 'META_ID', 'meta_similaridad_cos_normalized', 'META')
    fig3 = viz_1_distribucion_por_ods(df_indicador, 'INDICADOR_ID', 'indicador_similaridad_cos_normalized', 'INDICADOR')
    
    explicacion = """
    ## 📦 Diagrama de Caja por ODS
    
    ### ¿Qué muestra?
    Esta visualización muestra cómo se distribuyen los valores de similaridad para cada uno de los 17 ODS.
    
    ### ¿Cómo leerlo?
    - **Línea central**: Mediana (valor del medio)
    - **Caja**: Rango intercuartílico (Q1 a Q3)
    - **Líneas extendidas**: Valores mínimos y máximos normales
    - **Puntos fuera**: Valores atípicos (outliers)
    
    ### Interpretación:
    - ✅ **Cajas altas**: Mucha variación entre indicadores del ODS
    - ✅ **Cajas pequeñas**: Indicadores consistentes
    - ✅ **Mediana alta**: ODS muy relacionado con la iniciativa
    - ✅ **Puntos aislados**: Indicadores especialmente relevantes
    
    ### 💡 Consejo:
    Busca ODS con medianas altas y cajas pequeñas para identificar objetivos con indicadores consistentemente relevantes.
    """
    
    return fig1, fig2, fig3, explicacion

def tab_viz2(df_global):
# def tab_viz2():
    """Visualización 2: Heatmap ODS × Ranking"""
    if not DATOS_CARGADOS:
        return None, "⚠️ Error: No se pudieron cargar los datos."
    
    fig = viz_2_heatmap_ods_ranking(df_global)
    filepath = matplotlib_to_file(fig, 'viz2_heatmap.png')
    
    explicacion = """
    ## 🔥 Mapa de Calor: ODS × Ranking
    
    ### ¿Qué muestra?
    Matriz bidimensional que cruza los 17 ODS (filas) con deciles de ranking (columnas), 
    mostrando la similaridad promedio en cada celda.
    
    ### ¿Cómo leerlo?
    - 🔴 **Colores cálidos** (rojo/naranja): Alta similaridad
    - 🔵 **Colores fríos** (verde/azul): Baja similaridad
    - **D1 a D10**: Desde los más relevantes (D1) hasta los menos (D10)
    
    ### Interpretación:
    - ✅ **Fila roja completa**: ODS relevante en todos los rangos
    - ✅ **Columna roja**: Varios ODS relevantes en esa posición
    - ✅ **Diagonal descendente**: Patrón esperado (a mayor rank, menor similaridad)
    - ✅ **Rojo en D1-D2**: Los ODS más críticos
    
    ### 💡 Consejo:
    Identifica rápidamente qué ODS dominan en las posiciones altas del ranking.
    """
    
    return filepath, explicacion

def tab_viz3(df_global):
# def tab_viz3():
    """Visualización 3: Scatter 3D Interactivo"""
    if not DATOS_CARGADOS:
        return None, "⚠️ Error: No se pudieron cargar los datos."
    
    fig = viz_3_scatter_3d_interactivo(df_global)
    
    explicacion = """
    ## 🌐 Gráfico 3D Interactivo
    
    ### ¿Qué muestra?
    Visualización tridimensional donde cada punto representa un indicador.
    
    ### Las tres dimensiones:
    - **Eje X**: ODS ID (1-17)
    - **Eje Y**: Número de sub-indicador
    - **Eje Z**: Similaridad (altura del punto)
    - **Tamaño**: Los más grandes = más relevantes
    - **Color**: Cada ODS tiene su color
    
    ### Interactividad:
    - 🔄 **Rotar**: Arrastra con el mouse
    - 🔍 **Zoom**: Scroll o pinch
    - 👆 **Hover**: Pasa el mouse sobre puntos
    
    ### Interpretación:
    - ✅ **Puntos altos**: Alta similaridad
    - ✅ **Clusters de color**: Grupo de indicadores relacionados
    - ✅ **Puntos grandes y altos**: Los más importantes
    
    ### 💡 Consejo:
    Rota el gráfico para descubrir patrones ocultos y agrupaciones de indicadores.
    """
    
    return fig, explicacion

def tab_viz4(df_global):
# def tab_viz4():
    """Visualización 4: Radar Chart"""
    if not DATOS_CARGADOS:
        return None, "⚠️ Error: No se pudieron cargar los datos."
    
    fig = viz_4_radar_chart_ods(df_global)
    
    explicacion = """
    ## 🕸️ Gráfico de Radar (Perfil ODS)
    
    ### ¿Qué muestra?
    Gráfico circular que muestra el 'perfil ODS' de tu iniciativa con dos métricas.
    
    ### Cómo leerlo:
    - 🔵 **Polígono azul**: Similaridad promedio por ODS
    - 🔴 **Polígono rojo**: Similaridad máxima (mejor indicador)
    - **Distancia del centro**: Mayor distancia = mayor similaridad
    
    ### Interpretación:
    - ✅ **Picos hacia afuera**: ODS muy relevantes
    - ✅ **Valles hacia dentro**: ODS menos relacionados
    - ✅ **Forma circular**: Iniciativa equilibrada
    - ✅ **Forma irregular**: Especialización en ODS específicos
    - ✅ **Gap azul-rojo grande**: Indicador estrella en ese ODS
    
    ### 💡 Consejo:
    Ideal para presentaciones ejecutivas. Muestra de un vistazo el perfil completo de alineación ODS.
    """
    
    return fig, explicacion

def tab_viz5(df_global):
# def tab_viz5():
    """Visualización 5: Sunburst"""
    if not DATOS_CARGADOS:
        return None, "⚠️ Error: No se pudieron cargar los datos."
    
    fig = viz_5_sunburst_jerarquia(df_global)
    
    explicacion = """
    ## ☀️ Diagrama de Sol (Sunburst)
    
    ### ¿Qué muestra?
    Diagrama circular jerárquico mostrando ODS (centro) → Indicadores (anillo exterior).
    
    ### Cómo leerlo:
    - **Tamaño del segmento**: Proporcional a la similaridad
    - **Color**: Gradiente (más oscuro = mayor similaridad)
    - **Nivel 1 (centro)**: Los 17 ODS
    - **Nivel 2 (exterior)**: Indicadores individuales
    
    ### Interactividad:
    - 👆 **Click**: Zoom en un ODS específico
    - 🔍 **Hover**: Ver código y valor del indicador
    
    ### Interpretación:
    - ✅ **Segmentos grandes**: Indicadores muy relevantes
    - ✅ **ODS ocupa mucho espacio**: Muchos indicadores relevantes
    - ✅ **Colores oscuros**: Alta similaridad
    
    ### 💡 Consejo:
    Excelente para visualizar la contribución relativa de cada indicador al total.
    """
    
    return fig, explicacion

def tab_viz6(df_global):
# def tab_viz6():
    """Visualización 6: Top Indicadores por ODS"""
    if not DATOS_CARGADOS:
        return None, "⚠️ Error: No se pudieron cargar los datos."
    
    fig = viz_6_top_indicadores_por_ods(df_global, top_n=5)
    
    explicacion = """
    ## 🏆 Top 5 Indicadores por ODS
    
    ### ¿Qué muestra?
    Barras horizontales con los 5 indicadores más relevantes de cada ODS.
    
    ### Cómo leerlo:
    - **Longitud de barra**: Valor de similaridad
    - **Primera barra**: El indicador más relevante
    - **Color**: Gradiente por similaridad
    - **Cada panel**: Un ODS diferente
    
    ### Interpretación:
    - ✅ **Barra mucho más larga**: Indicador campeón
    - ✅ **Barras parejas**: Varios indicadores igualmente relevantes
    - ✅ **Comparación entre ODS**: Qué objetivo tiene mejores indicadores
    
    ### 💡 Consejo:
    Perfecta para planificación estratégica. Te dice exactamente en qué indicadores enfocarte por cada ODS.
    """
    
    return fig, explicacion

def tab_viz7(df_global):
# def tab_viz7():
    """Visualización 7: Stream Graph"""
    if not DATOS_CARGADOS:
        return None, "⚠️ Error: No se pudieron cargar los datos."
    
    fig = viz_7_streamgraph_similaridad(df_global)
    
    explicacion = """
    ## 🌊 Gráfico de Flujo (Stream Graph)
    
    ### ¿Qué muestra?
    Áreas apiladas que muestran cómo cambia la contribución porcentual de cada ODS 
    a lo largo del ranking.
    
    ### Cómo leerlo:
    - **Eje horizontal**: Ranking agrupado (izq. = más relevante)
    - **Eje vertical**: Porcentaje de contribución (suma 100%)
    - **Ancho del color**: Porcentaje del ODS en ese rango
    
    ### Interpretación:
    - ✅ **Color dominante izquierda**: ODS líder en indicadores relevantes
    - ✅ **Cambio de color**: Transición de relevancia
    - ✅ **Área ancha constante**: ODS presente en todo el ranking
    - ✅ **Área que crece/decrece**: ODS relevante en ciertos rangos
    
    ### 💡 Consejo:
    Si un ODS ocupa mucho espacio a la izquierda, domina entre los indicadores más relevantes.
    """
    
    return fig, explicacion

def tab_viz8(df_global):
# def tab_viz8():
    """Visualización 8: Violin Plot"""
    if not DATOS_CARGADOS:
        return None, "⚠️ Error: No se pudieron cargar los datos."
    
    fig = viz_8_violin_plot_ods(df_global)
    
    explicacion = """
    ## 🎻 Gráfico de Violín
    
    ### ¿Qué muestra?
    Similar al diagrama de caja pero con más detalle. Muestra la 'forma' completa 
    de la distribución de similaridad por ODS.
    
    ### Cómo leerlo:
    - **Ancho del violín**: Concentración de valores
    - **Caja interior**: Mediana y cuartiles
    - **Línea horizontal**: Media (promedio)
    
    ### Concepto clave:
    El ancho representa la **densidad de probabilidad**: donde el violín es más ancho, 
    es más probable encontrar indicadores con esos valores.
    
    ### Interpretación:
    - ✅ **Violín ancho en un punto**: Muchos indicadores similares
    - ✅ **Dos ensanchamientos**: Dos grupos distintos
    - ✅ **Violín delgado**: Pocos indicadores en ese rango
    - ✅ **Forma simétrica**: Distribución equilibrada
    
    ### 💡 Consejo:
    Detecta distribuciones complejas que el diagrama de caja no puede mostrar.
    """
    
    return fig, explicacion

def tab_viz9(df_global):
# def tab_viz9():
    """Visualización 9: Dashboard Integrado"""
    if not DATOS_CARGADOS:
        return None, "⚠️ Error: No se pudieron cargar los datos."
    
    fig = viz_9_dashboard_metricas(df_global)
    
    explicacion = """
    ## 📊 Dashboard Integrado (4 Paneles)
    
    ### Panel 1 (Superior Izquierdo): Top 10 Indicadores
    Barras con los 10 indicadores más relevantes del análisis completo.
    
    ### Panel 2 (Superior Derecho): Estadísticas por ODS
    Tabla con media, desviación estándar, mínimo, máximo y cantidad por ODS.
    
    ### Panel 3 (Inferior Izquierdo): Histograma Global
    Distribución de frecuencias de todos los valores de similaridad.
    
    ### Panel 4 (Inferior Derecho): Correlación Rank-Similaridad
    Scatter plot con línea de tendencia. **CRÍTICO para validación del sistema**.
    
    ### Validación:
    - ✅ **Línea descendente**: Sistema funcionando correctamente
    - ✅ **Correlación < -0.7**: Excelente
    - ⚠️ **Correlación > -0.4**: Revisar sistema
    
    ### 💡 Consejo:
    Este debe ser tu punto de partida. Vista 360° del análisis completo.
    """
    
    return fig, explicacion

def tab_viz10(df_global):
# def tab_viz10():
    """Visualización 10: Matriz de Transición"""
    if not DATOS_CARGADOS:
        return None, "⚠️ Error: No se pudieron cargar los datos."
    
    fig = viz_10_matriz_transicion(df_global)
    filepath = matplotlib_to_file(fig, 'viz10_matriz_transicion.png')
    
    explicacion = """
    ## 🔀 Matriz de Transición por Cuartiles
    
    ### ¿Qué muestra?
    Mapa de calor que muestra el porcentaje de cada ODS presente en los 4 cuartiles del ranking.
    
    ### Cómo leerlo:
    - **Filas**: Los 17 ODS
    - **Columnas**: Q1 (Top 25%), Q2, Q3, Q4 (Bottom 25%)
    - **Valores**: Porcentaje de presencia del ODS
    - **Colores**: Naranja/rojo = alta presencia
    
    ### Interpretación:
    - ✅ **Rojo intenso en Q1**: ODS crítico (domina rankings altos)
    - ✅ **Colores uniformes**: ODS consistente en todo el ranking
    - ✅ **Concentración en un cuartil**: ODS especializado
    - ✅ **Claro en Q1, oscuro en Q4**: Más relevante en posiciones bajas
    
    ### 💡 Consejo:
    Analiza la consistencia de relevancia por ODS. Alta presencia en Q1 = crítico para la iniciativa.
    """
    
    return filepath, explicacion

def tab_estadisticas(df_global):
# def tab_estadisticas():
    """Pestaña con análisis estadístico detallado"""
    if not DATOS_CARGADOS:
        return "⚠️ Error: No se pudieron cargar los datos."
    
    # Estadísticas globales
    stats = df_global['similaridad_cos'].describe()
    correlacion = df_global['rank'].corr(df_global['similaridad_cos'])
    
    # Por ODS
    stats_ods = df_global.groupby('ods_id')['similaridad_cos'].agg([
        ('count', 'count'),
        ('mean', 'mean'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max')
    ]).round(4)
    
    # Top 50
    top_50_ods = df_global.nsmallest(50, 'rank')['ods_id'].value_counts()
    
    html = f"""
    <div style="font-family: Arial, sans-serif; padding: 20px;">
        <h1 style="color: #2E5090;">📈 Análisis Estadístico Detallado</h1>
        
        <div class="stats-box" style="background-color: #E8F4F8; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h2 style="color: #2E5090;">1. Estadísticas Globales</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Cantidad de datos:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats['count']:.0f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Media:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats['mean']:.4f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Desviación Estándar:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats['std']:.4f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Mínimo:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats['min']:.4f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Q1 (Percentil 25):</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats['25%']:.4f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Mediana (Q2):</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats['50%']:.4f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Q3 (Percentil 75):</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats['75%']:.4f}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>Máximo:</strong></td>
                    <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{stats['max']:.4f}</td>
                </tr>
            </table>
        </div>
        
        <div class="explanation-box" style="background-color: #{'E6F7E6' if correlacion < -0.7 else 'FFF9E6'}; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #{'28A745' if correlacion < -0.7 else 'FFD700'};">
            <h2 style="color: #{'28A745' if correlacion < -0.7 else 'FF8C00'};">2. Validación del Sistema</h2>
            <p style="font-size: 18px;"><strong>Correlación Rank vs Similaridad:</strong> {correlacion:.4f}</p>
            <p><strong>Interpretación:</strong> 
            {
                "✅ Excelente - Sistema de ranking muy confiable" if correlacion < -0.9 else
                "✅ Muy bueno - Sistema de ranking confiable" if correlacion < -0.7 else
                "⚠️ Aceptable - Sistema funciona pero puede mejorarse" if correlacion < -0.4 else
                "❌ Problema - Revisar cálculo de similaridad o ranking"
            }
            </p>
            <p><em>Una correlación negativa fuerte indica que a mayor ranking (menos relevante), menor es la similaridad, lo cual es el comportamiento esperado.</em></p>
        </div>
        
        <div class="stats-box" style="background-color: #FFF9E6; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h2 style="color: #2E5090;">3. Estadísticas por ODS</h2>
            <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                <thead>
                    <tr style="background-color: #FFD700;">
                        <th style="padding: 10px; text-align: left;">ODS</th>
                        <th style="padding: 10px; text-align: right;">Count</th>
                        <th style="padding: 10px; text-align: right;">Media</th>
                        <th style="padding: 10px; text-align: right;">Std</th>
                        <th style="padding: 10px; text-align: right;">Min</th>
                        <th style="padding: 10px; text-align: right;">Max</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''<tr>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>ODS {idx}</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{int(row['count'])}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{row['mean']:.4f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{row['std']:.4f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{row['min']:.4f}</td>
                        <td style="padding: 8px; border-bottom: 1px solid #ddd; text-align: right;">{row['max']:.4f}</td>
                    </tr>''' for idx, row in stats_ods.iterrows()])}
                </tbody>
            </table>
        </div>
        
        <div class="explanation-box" style="background-color: #E8F4F8; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #2E5090;">
            <h2 style="color: #2E5090;">4. ODS Más Representados en Top 50</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background-color: #4472C4; color: white;">
                        <th style="padding: 10px; text-align: left;">ODS</th>
                        <th style="padding: 10px; text-align: right;">Cantidad</th>
                        <th style="padding: 10px; text-align: right;">Porcentaje</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''<tr>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd;"><strong>ODS {idx}</strong></td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{count}</td>
                        <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">{count/50*100:.1f}%</td>
                    </tr>''' for idx, count in top_50_ods.head(10).items()])}
                </tbody>
            </table>
        </div>
    </div>
    """
    
    return html

# ============================================================================
# CONSTRUCCIÓN DE LA APLICACIÓN GRADIO
# ============================================================================

def crear_app():
    """Crea y configura la aplicación Gradio completa"""
    
    with gr.Blocks(
        title="Sistema de Visualización ODS",
        theme=gr.themes.Soft(
            primary_hue="indigo",
            secondary_hue="orange",
            neutral_hue="slate"
        ),
        css=CUSTOM_CSS
    ) as app:

        gr.HTML(f"""
        <div class="header-institucional">
            <div style="flex: 0 0 auto;">
                <img src="{dict_logos['gobierno']}" 
                     alt="Gobierno de Colombia" 
                     class="logo-institucional">
            </div>
            <div class="titulo-institucional">
                <h1></h1>
                <p> </p>
            </div>
            <div style="flex: 0 0 auto;">
                <img src="{dict_logos['fondo_un']}" 
                     alt="Fondo Multidonante de las Naciones Unidas" 
                     class="logo-institucional">
            </div>
        </div>
        """)
        
        # Encabezado principal
        gr.Markdown("""
        # 📊 Voces ODS: Explora cómo tu voz conecta con los ODS
        ### Explorador Interactivo
        
        *Voces ODS es una herramienta innovadora que traduce las narrativas de las comunidades en lenguaje de los Objetivos de Desarrollo Sostenible (ODS). Su propósito es visibilizar cómo las voces locales, las memorias colectivas como las iniciativas PATR y las experiencias territoriales se vinculan con las metas globales, facilitando el análisis e incidencia para la toma de decisiones.A través de un sistema de visualización y análisis de similitud, la herramienta permite identificar líneas estratégicas asociadas a las narrativas de las comunidades, transformando relatos en insumos estratégicos para políticas públicas, proyectos de desarrollo y procesos de incidencia*
        """)
        
        # Pestañas principales
        with gr.Tabs():

            # PESTAÑA: CONSULTA
            with gr.Tab("CONSULTA BASICA"):
                with gr.Column():
                  query_in = gr.Textbox(lines=5, placeholder="Escribe aquí tu consulta...", label="Iniciativa a analizar")
                  query_out = gr.Textbox(lines=5, label="Texto ajustado para lenguaje natural", visible=False)
                
                btn = gr.Button(value="Analizar mi iniciativa")
                
                with gr.Row():
                  ods = gr.Dataframe(type="pandas", label="ODS")
                  meta = gr.Dataframe(type="pandas", label="METAS")
                  indicador = gr.Dataframe(type="pandas", label="INDICADORES")                   

                with gr.Row():
                  genero = gr.Dataframe(type="pandas", label="Enfoque de genero")
                  poblacional = gr.Dataframe(type="pandas", label="Enfoque poblacional")
                  etnico = gr.Dataframe(type="pandas", label="Enfoque étnico")

                with gr.Row():
                  pilar = gr.Dataframe(type="pandas", label="Pilares")
                  estrategia = gr.Dataframe(type="pandas", label="Estrategias")
                  categoria = gr.Dataframe(type="pandas", label="Categorias") 
                
                with gr.Row():
                  bdl_ods = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="BDL_ODS")

                  # query_in.render()
                  # indicador, indicador_norm, query, pilares, estrategias, categorias = search()

                
                btn.click(search, query_in, [query_out,ods,meta,indicador,genero,poblacional,etnico,pilar,estrategia,categoria,bdl_ods])
                # btn.click(cara_utility, [a_valu, trials], cara_output)
                
            with gr.Tab('CONSULTA ESPECIALIZADA'):

              # with gr.Tab("CONSULTA"): 

                with gr.Column():
                  query_in_esp = gr.Textbox(lines=5, placeholder="Escribe aquí tu consulta...", label="Iniciativa a analizar")
                  query_out_esp = gr.Textbox(lines=5, label="Texto ajustado para lenguaje natural", visible=False)
                
                btn_esp = gr.Button(value="Analizar mi iniciativa")
                

                # lvl = gr.Dropdown([col for col in bdl_ods_esp.value.columns if 'ID' in col], label='Nivel de análisis')
                # score = gr.Dropdown([col for col in bdl_ods_esp.value.columns if 'similaridad' in col], label='Score de medida')  
                # rank = gr.Dropdown([col for col in bdl_ods_esp.value.columns if 'rank' in col], label='Score de medida')    

                with gr.Tab("Clasificaciones"):
                  with gr.Row():
                    ods_esp = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="ODS")
                    meta_esp = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="METAS")
                    indicador_esp = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="INDICADORES")                   

                  with gr.Row():
                    genero_esp = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="Enfoque de genero")
                    poblacional_esp = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="Enfoque poblacional")
                    etnico_esp = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="Enfoque étnico")

                  with gr.Row():
                    pilar_esp = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="Pilares")
                    estrategia_esp = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="Estrategias")
                    categoria_esp = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="Categorias") 
                  
                  with gr.Row():
                    bdl_ods_esp = gr.Dataframe(value=pd.DataFrame(),type="pandas", label="ODS")

                # PESTAÑA: INICIO
                with gr.Tab("🏠 Inicio"):
                    html_inicio_ods = gr.HTML() #tab_inicio(ods.value)
                    

                    btn0 = gr.Button("🔄 Generar Metricas Iniciales", variant="primary")
                    btn0.click(
                        fn=tab_inicio,
                        inputs=[ods_esp,meta_esp,indicador_esp],
                        outputs=[html_inicio_ods]
                    )
                    
                
                # PESTAÑA 1: BOX PLOT
                with gr.Tab("📦 1. Box Plot"):
                    btn1 = gr.Button("🔄 Generar Visualización", variant="primary")
                    with gr.Row():                        
                        with gr.Column(scale=1):
                            exp1 = gr.Markdown()
                    with gr.Row(visible=False):
                        with gr.Column(scale=2):
                            plot1_1 = gr.Plot(label="Diagrama de Caja por ODS")
                        
                    with gr.Row():
                        with gr.Column(scale=2):
                            plot1_2 = gr.Plot(label="Diagrama de Caja por META")
                        
                    with gr.Row():
                        with gr.Column(scale=2):
                            plot1_3 = gr.Plot(label="Diagrama de Caja por INDICADOR")
                        
                    
                    
                    btn1.click(
                        fn=tab_viz1,
                        inputs=[ods_esp, meta_esp, indicador_esp],
                        outputs=[plot1_1, plot1_2, plot1_3, exp1]
                    )
                
                # PESTAÑA 2: HEATMAP
                with gr.Tab("🔥 2. Heatmap"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            img2 = gr.Image(label="Mapa de Calor ODS × Ranking", type="filepath")
                        with gr.Column(scale=1):
                            exp2 = gr.Markdown()
                    
                    btn2 = gr.Button("🔄 Generar Visualización", variant="primary")
                    btn2.click(
                        fn=tab_viz2,
                        inputs=[ods],
                        outputs=[img2, exp2]
                    )
                
                # PESTAÑA 3: SCATTER 3D
                with gr.Tab("🌐 3. Scatter 3D"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            plot3 = gr.Plot(label="Gráfico 3D Interactivo")
                        with gr.Column(scale=1):
                            exp3 = gr.Markdown()
                    
                    btn3 = gr.Button("🔄 Generar Visualización", variant="primary")
                    btn3.click(
                        fn=tab_viz3,
                        inputs=[ods],
                        outputs=[plot3, exp3]
                    )
                
                # PESTAÑA 4: RADAR
                with gr.Tab("🕸️ 4. Radar Chart"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            plot4 = gr.Plot(label="Gráfico de Radar")
                        with gr.Column(scale=1):
                            exp4 = gr.Markdown()
                    
                    btn4 = gr.Button("🔄 Generar Visualización", variant="primary")
                    btn4.click(
                        fn=tab_viz4,
                        inputs=[ods],
                        outputs=[plot4, exp4]
                    )
                
                # PESTAÑA 5: SUNBURST
                with gr.Tab("☀️ 5. Sunburst"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            plot5 = gr.Plot(label="Diagrama de Sol")
                        with gr.Column(scale=1):
                            exp5 = gr.Markdown()
                    
                    btn5 = gr.Button("🔄 Generar Visualización", variant="primary")
                    btn5.click(
                        fn=tab_viz5,
                        inputs=[ods],
                        outputs=[plot5, exp5]
                    )
                
                # PESTAÑA 6: TOP INDICADORES
                with gr.Tab("🏆 6. Top Indicadores"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            plot6 = gr.Plot(label="Top 5 Indicadores por ODS")
                        with gr.Column(scale=1):
                            exp6 = gr.Markdown()
                    
                    btn6 = gr.Button("🔄 Generar Visualización", variant="primary")
                    btn6.click(
                        fn=tab_viz6,
                        inputs=[ods],
                        outputs=[plot6, exp6]
                    )
                
                # PESTAÑA 7: STREAM GRAPH
                with gr.Tab("🌊 7. Stream Graph"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            plot7 = gr.Plot(label="Gráfico de Flujo")
                        with gr.Column(scale=1):
                            exp7 = gr.Markdown()
                    
                    btn7 = gr.Button("🔄 Generar Visualización", variant="primary")
                    btn7.click(
                        fn=tab_viz7,
                        inputs=[ods],
                        outputs=[plot7, exp7]
                    )
                
                # PESTAÑA 8: VIOLIN PLOT
                with gr.Tab("🎻 8. Violin Plot"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            plot8 = gr.Plot(label="Gráfico de Violín")
                        with gr.Column(scale=1):
                            exp8 = gr.Markdown()
                    
                    btn8 = gr.Button("🔄 Generar Visualización", variant="primary")
                    btn8.click(
                        fn=tab_viz8,
                        inputs=[ods],
                        outputs=[plot8, exp8]
                    )
                
                # PESTAÑA 9: DASHBOARD
                with gr.Tab("📊 9. Dashboard"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            plot9 = gr.Plot(label="Dashboard Integrado")
                        with gr.Column(scale=1):
                            exp9 = gr.Markdown()
                    
                    btn9 = gr.Button("🔄 Generar Visualización", variant="primary")
                    btn9.click(
                        fn=tab_viz9,
                        inputs=[ods],
                        outputs=[plot9, exp9]
                    )
                
                # PESTAÑA 10: MATRIZ TRANSICIÓN
                with gr.Tab("🔀 10. Matriz Transición"):
                    with gr.Row():
                        with gr.Column(scale=2):
                            img10 = gr.Image(label="Matriz de Transición", type="filepath")
                        with gr.Column(scale=1):
                            exp10 = gr.Markdown()
                    
                    btn10 = gr.Button("🔄 Generar Visualización", variant="primary")
                    btn10.click(
                        fn=tab_viz10,
                        inputs=[ods],
                        outputs=[img10, exp10]
                    )
                
                # PESTAÑA: ESTADÍSTICAS
                with gr.Tab("📈 Estadísticas"):
                    html_stats = gr.HTML() #tab_estadisticas(ods)

                    btn11 = gr.Button("🔄 Generar Estadísticas", variant="primary")
                    btn11.click(
                        fn=tab_estadisticas,
                        inputs=[ods],
                        outputs=[html_stats]
                    )
                  
                btn_esp.click(search, query_in_esp, [query_out_esp,ods_esp,meta_esp,indicador_esp,genero_esp,poblacional_esp,etnico_esp,pilar_esp,estrategia_esp,categoria_esp,bdl_ods_esp])

                
          
        # Pie de página
        gr.Markdown("""
        ---
        ### 📚 Recursos Adicionales
        - **Documentación completa**: Consulta los archivos `.md` incluidos
        - **Código fuente**: `visualizaciones_ods.py`
        - **Documento Word**: `GUIA_VISUALIZACIONES_PUBLICO_GENERAL.docx`
        
        ---
        *Sistema de Visualización ODS | Octubre 2025 | Desarrollado con Python, Plotly, Matplotlib y Gradio*
        """)
    
    return app

# ============================================================================
# EJECUCIÓN DE LA APLICACIÓN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("INICIANDO APLICACIÓN GRADIO - VISUALIZACIONES ODS")
    print("="*70)
    
    # if not DATOS_CARGADOS:
    #     print("\n⚠️  ADVERTENCIA: No se pudieron cargar los datos.")
    #     print("    Verifica que el archivo existe en:", RUTA_DATOS)
    #     print("    La aplicación se iniciará pero mostrará errores.")
    # else:
    #     print(f"\n✓ Datos cargados correctamente: {len(df_global)} registros")
    #     print(f"✓ ODS únicos: {df_global['ods_id'].nunique()}")
    
    print("\n" + "="*70)
    print("CREANDO APLICACIÓN...")
    print("="*70)
    
    app = crear_app()
    
    print("\n✓ Aplicación creada exitosamente")
    print("\n" + "="*70)
    print("INICIANDO SERVIDOR WEB...")
    print("="*70)
    print("\n🌐 La aplicación se abrirá en tu navegador automáticamente")
    print("📍 URL local: http://127.0.0.1:7860")
    print("🌍 URL pública: Se generará si share=True\n")
    print("💡 Presiona Ctrl+C para detener el servidor\n")
    
    # Lanzar la aplicación
    app.launch(
        # server_name="0.0.0.0",  # Permite acceso desde cualquier IP
        # server_port=7860,        # Puerto por defecto
        share=True,             # Cambiar a True para URL pública
        # show_error=True,         # Mostrar errores en la interfaz
        # quiet=False              # Mostrar logs en consola
    )
