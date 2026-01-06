"""
VISUALIZACIONES PARA ANÁLISIS DE SIMILARIDAD COSENO - INDICADORES ODS
========================================================================

Este script genera visualizaciones interactivas y estáticas para ponderar
el valor de similaridad_cos como proxy de similaridad al consultar una
iniciativa ciudadana con una base de indicadores ODS.

Autor: Análisis ODS
Fecha: Octubre 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.gridspec import GridSpec
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import warnings

warnings.filterwarnings('ignore')

# Configuración estética
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# 1. CARGA Y PREPARACIÓN DE DATOS
# ============================================================================

def cargar_datos(ruta_archivo):
    """
    Carga los datos desde el archivo markdown y los convierte a DataFrame
    """
    # Leer el archivo saltando la línea de separación
    df = pd.read_csv(ruta_archivo, sep='|', skiprows=[1])
    
    # Limpiar columnas (eliminar espacios)
    df.columns = df.columns.str.strip()
    
    # Eliminar columnas vacías (primera y última por el formato markdown)
    df = df.drop(df.columns[[0, -1]], axis=1)
    
    # Limpiar espacios en valores de texto
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    
    return df


# ============================================================================
# 2. GRÁFICA 1: DISTRIBUCIÓN DE SIMILARIDAD POR ODS (Box Plot Interactivo)
# ============================================================================

def viz_1_distribucion_por_ods(df, id_lvl, score, titulo):
    """
    LÓGICA: Esta visualización muestra la distribución de valores de similaridad
    coseno agrupados por cada ODS. Permite identificar:
    - Qué ODS tienen mayor rango de similaridad
    - La mediana de similaridad por ODS
    - Outliers o valores atípicos
    - Consistencia interna de cada ODS
    
    INTERPRETACIÓN:
    - Cajas más altas → Mayor variabilidad en la similaridad dentro del ODS
    - Medianas altas → El ODS tiene indicadores más similares a la consulta
    - Outliers superiores → Indicadores específicos muy relevantes
    """
    
    fig = go.Figure()
    
    for idx, ods in enumerate(sorted(df['ODS_ID'].unique())):
        datos_ods = df[df['ODS_ID'] == ods][score]
        
        fig.add_trace(go.Box(
            y=datos_ods,
            name=f'ODS {ods}',
            boxmean='sd',  # Mostrar media y desviación estándar
            marker_color=px.colors.qualitative.Plotly[int(ods) % len(px.colors.qualitative.Plotly)]
        ))
    
    fig.update_layout(
        title={
            'text': f'Distribución de Similaridad Coseno por {titulo}<br><sub>Análisis de dispersión y tendencia central por objetivo</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        # xaxis_title='Objetivo de Desarrollo Sostenible',
        xaxis_title=id_lvl,
        yaxis_title='Similaridad Coseno',
        height=600,
        showlegend=False,
        hovermode='x unified'
    )
    
    return fig


# ============================================================================
# 3. GRÁFICA 2: HEATMAP DE SIMILARIDAD (ODS vs Rango de Ranking)
# ============================================================================

def viz_2_heatmap_ods_ranking(df, id_lvl, score, rank, titulo):
    """
    LÓGICA: Matriz de calor que muestra la intensidad de similaridad en función
    de dos dimensiones: ODS (eje Y) y posición en el ranking (eje X agrupado).
    
    Se divide el ranking en deciles (10 grupos) para visualizar cómo se
    distribuye la similaridad a lo largo de la relevancia ordenada.
    
    INTERPRETACIÓN:
    - Colores cálidos (rojo/naranja) → Alta similaridad
    - Colores fríos (azul) → Baja similaridad
    - Patrón horizontal → Un ODS domina en ciertas posiciones
    - Patrón vertical → Ciertas posiciones tienen alta similaridad en varios ODS
    - Diagonal descendente → Comportamiento esperado (mayor rank → menor similaridad)
    """
    
    # Crear deciles de ranking
    df['rank_decil'] = pd.qcut(df[rank], q=10, labels=[f'D{i+1}' for i in range(10)])
    
    # Crear matriz pivote
    pivot_table = df.pivot_table(
        values=score,
        index=id_lvl,
        columns='rank_decil',
        aggfunc='mean'
    )
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    sns.heatmap(
        pivot_table,
        annot=True,
        fmt='.3f',
        cmap='RdYlGn',
        center=df[score].median(),
        cbar_kws={'label': 'Similaridad Coseno Promedio'},
        linewidths=0.5,
        ax=ax
    )
    
    ax.set_title(
        f'Heatmap: Similaridad Coseno por {id_lvl} y Decil de Ranking\n'
        'Visualización de patrones de relevancia en función del orden',
        fontsize=14,
        pad=20
    )
    ax.set_xlabel('Decil de Ranking (D1=Top 10%, D10=Bottom 10%)', fontsize=12)
    ax.set_ylabel(id_lvl, fontsize=12)
    
    plt.tight_layout()
    return fig


# ============================================================================
# 4. GRÁFICA 3: SCATTER PLOT 3D (ODS, Indicador, Similaridad)
# ============================================================================

def viz_3_scatter_3d_interactivo(df, id_lvl, score, rank, titulo):
    """
    LÓGICA: Visualización tridimensional que permite explorar la relación
    entre tres variables:
    - Eje X: ODS ID
    - Eje Y: Número de indicador dentro del ODS (extraído del indicador_id)
    - Eje Z: Similaridad coseno
    - Tamaño: Inversamente proporcional al ranking (más relevantes = más grandes)
    - Color: Por ODS
    
    INTERPRETACIÓN:
    - Puntos altos (eje Z) → Alta similaridad
    - Clusters verticales → Varios indicadores de un ODS son similares
    - Puntos grandes en altura → Indicadores relevantes y bien posicionados
    - Permite rotar e interactuar para descubrir patrones espaciales
    """
    
    # Extraer número de indicador
    df['indicador_num'] = df[id_lvl].str.extract(r'\.(\d+)\.').astype(float)
    
    fig = go.Figure()
    
    for ods in sorted(df['ODS_ID'].unique()):
        datos_ods = df[df['ODS_ID'] == ods]
        
        fig.add_trace(go.Scatter3d(
            x=datos_ods['ODS_ID'],
            y=datos_ods['indicador_num'],
            z=datos_ods[score],
            mode='markers',
            name=f'ODS {ods}',
            marker=dict(
                size=10 - (datos_ods[rank] / len(df) * 8),  # Tamaño inversamente proporcional al rank
                opacity=0.7,
                line=dict(width=0.5, color='white')
            ),
            text=datos_ods[id_lvl],
            hovertemplate='<b>%{text}</b><br>' +
                          'ODS: %{x}<br>' +
                          'Similaridad: %{z:.4f}<br>' +
                          '<extra></extra>'
        ))
    
    fig.update_layout(
        title='Visualización 3D: ODS × Indicador × Similaridad<br><sub>Exploración espacial de patrones de relevancia</sub>',
        scene=dict(
            xaxis_title='ODS ID',
            yaxis_title='Número de Indicador',
            zaxis_title='Similaridad Coseno',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        height=700,
        showlegend=True
    )
    
    return fig


# ============================================================================
# 5. GRÁFICA 4: RADAR CHART - Similaridad Promedio por ODS
# ============================================================================

def viz_4_radar_chart_ods(df, id_lvl, score, rank, titulo):
    """
    LÓGICA: Gráfico de radar (spider chart) que muestra la similaridad promedio
    de cada ODS en forma circular. Útil para comparar rápidamente el perfil
    de relevancia de todos los ODS.
    
    INTERPRETACIÓN:
    - Áreas más grandes → Mayor similaridad promedio con la consulta
    - Forma del polígono → Perfil de cobertura de la iniciativa
    - Picos → ODS altamente relevantes
    - Valles → ODS menos relacionados
    - Simetría → Iniciativa balanceada entre ODS vs. especializada
    """
    
    # Calcular promedios por ODS
    ods_stats = df.groupby(id_lvl).agg({
        score: ['mean', 'max', 'count']
    }).reset_index()
    
    ods_stats.columns = [id_lvl, 'sim_promedio', 'sim_max', 'count_indicadores']
    ods_stats = ods_stats.sort_values(id_lvl)
    
    fig = go.Figure()
    
    # Similaridad promedio
    fig.add_trace(go.Scatterpolar(
        r=ods_stats['sim_promedio'],
        theta=['ODS ' + str(x) for x in ods_stats[id_lvl]],
        fill='toself',
        name='Similaridad Promedio',
        line_color='blue',
        fillcolor='rgba(0, 0, 255, 0.2)'
    ))
    
    # Similaridad máxima
    fig.add_trace(go.Scatterpolar(
        r=ods_stats['sim_max'],
        theta=['ODS ' + str(x) for x in ods_stats[id_lvl]],
        fill='toself',
        name='Similaridad Máxima',
        line_color='red',
        fillcolor='rgba(255, 0, 0, 0.1)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0.85, 0.95]  # Ajustar según datos reales
            )
        ),
        title=f'Radar Chart: Perfil de Similaridad por {titulo}<br><sub>Comparación de promedios y máximos</sub>',
        showlegend=True,
        height=600
    )
    
    return fig


# ============================================================================
# 6. GRÁFICA 5: SUNBURST - Jerarquía ODS → Indicadores
# ============================================================================

def viz_5_sunburst_jerarquia(df, id_lvl, score, rank, titulo):
    """
    LÓGICA: Diagrama de sunburst (sol radiante) que muestra la jerarquía
    ODS → Indicadores con el tamaño proporcional a la similaridad.
    
    El círculo interior representa los ODS y los anillos exteriores los
    indicadores dentro de cada ODS.
    
    INTERPRETACIÓN:
    - Segmentos grandes → Indicadores o grupos de indicadores muy similares
    - Colores → Gradiente de similaridad (más oscuro = mayor similaridad)
    - Permite drill-down interactivo
    - Visualiza la contribución relativa de cada indicador al ODS
    """
    
    # Preparar datos para sunburst
    df_sun = df.copy()
    df_sun['ods_label'] = 'ODS ' + df_sun['ODS_ID'].astype(str)
    df_sun['path'] = df_sun['ods_label'] + ' / ' + df_sun[id_lvl]
    
    # Limitar a top 100 para mejor visualización
    df_sun_top = df_sun.nsmallest(100, rank)
    
    fig = px.sunburst(
        df_sun_top,
        path=['ods_label', id_lvl],
        values=score,
        color=score,
        color_continuous_scale='Viridis',
        hover_data=[rank],
        title=f'Sunburst: Jerarquía {titulo} → Indicadores (Top 100)<br><sub>Tamaño proporcional a similaridad</sub>'
    )
    
    fig.update_layout(
        height=700,
        coloraxis_colorbar=dict(title="Similaridad")
    )
    
    return fig


# ============================================================================
# 7. GRÁFICA 6: CASCADA - Top Indicadores por ODS
# ============================================================================

def viz_6_top_indicadores_por_ods(df, id_lvl, score, rank, titulo, top_n=3):
    """
    LÓGICA: Para cada ODS, muestra los top N indicadores con mayor similaridad
    en un formato de barras horizontales agrupadas.
    
    Permite comparar:
    - Cuál es el mejor indicador de cada ODS
    - La brecha entre el mejor y los siguientes
    - Qué ODS tiene los indicadores más relevantes en general
    
    INTERPRETACIÓN:
    - Barras más largas → Mayor similaridad
    - Agrupación densa → Varios indicadores igualmente relevantes
    - Gaps grandes → Un indicador destaca sobre el resto en ese ODS
    """
    
    # Obtener top N por ODS
    top_indicadores = df.groupby('ODS_ID').apply(
        lambda x: x.nsmallest(top_n, rank)
    ).reset_index(drop=True)
    
    fig = px.bar(
        top_indicadores,
        x=score,
        y=id_lvl,
        color=id_lvl,
        orientation='h',
        facet_row=id_lvl,
        height=300 * len(df[id_lvl].unique()) // 3,
        title=f'Top {top_n} Indicadores con Mayor Similaridad por ODS<br><sub>Análisis de relevancia por objetivo</sub>',
        labels={score: 'Similaridad Coseno', id_lvl: 'Indicador'},
        color_continuous_scale='Plasma'
    )
    
    fig.update_yaxes(showticklabels=True, matches=None)
    fig.update_xaxes(matches='x')
    
    return fig


# ============================================================================
# 8. GRÁFICA 7: STREAM GRAPH - Evolución de Similaridad
# ============================================================================

def viz_7_streamgraph_similaridad(df, id_lvl, score, rank, titulo):
    """
    LÓGICA: Gráfico de área apilada que muestra cómo contribuye cada ODS
    a la similaridad acumulada a lo largo del ranking.
    
    El eje X es el ranking (ordenado) y el eje Y muestra el área acumulada
    de similaridad por ODS.
    
    INTERPRETACIÓN:
    - Áreas más anchas → ODS con mayor presencia en ese rango de ranking
    - Cambios de color dominante → Transición de relevancia entre ODS
    - Posición en ranking bajo → Indicadores más relevantes
    - Permite ver qué ODS domina en qué rangos de relevancia
    """
    
    # Crear bins de ranking
    df['rank_bin'] = pd.cut(df[rank], bins=20, labels=False)
    
    # Agrupar por rank_bin y ODS
    stream_data = df.groupby(['rank_bin', id_lvl])[score].sum().reset_index()
    
    # Pivotar para streamgraph
    stream_pivot = stream_data.pivot(index='rank_bin', columns=id_lvl, values=score).fillna(0)
    
    fig = go.Figure()
    
    for ods in stream_pivot.columns:
        fig.add_trace(go.Scatter(
            x=stream_pivot.index,
            y=stream_pivot[ods],
            mode='lines',
            name=f'ODS {ods}',
            stackgroup='one',
            groupnorm='percent',  # Normalizar a porcentaje
            hovertemplate='ODS %{fullData.name}<br>Contribución: %{y:.1f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title='Stream Graph: Contribución de cada ODS por Rango de Ranking<br><sub>Evolución de relevancia normalizada</sub>',
        xaxis_title='Rango de Ranking (agrupado)',
        yaxis_title='Contribución Porcentual',
        height=600,
        hovermode='x unified'
    )
    
    return fig


# ============================================================================
# 9. GRÁFICA 8: VIOLIN PLOT - Comparación Detallada de Distribuciones
# ============================================================================

def viz_8_violin_plot_ods(df, id_lvl, score, rank, titulo):
    """
    LÓGICA: Similar al box plot pero muestra la distribución completa de
    densidad de probabilidad de la similaridad para cada ODS.
    
    El ancho del "violín" representa la concentración de valores en ese rango.
    
    INTERPRETACIÓN:
    - Violines anchos → Muchos valores en ese rango de similaridad
    - Violines angostos → Pocos valores en ese rango
    - Forma bimodal → Dos grupos de indicadores con diferente similaridad
    - Forma unimodal → Indicadores homogéneos en similaridad
    - Permite ver distribuciones no normales que el box plot no captura
    """
    
    fig = go.Figure()
    
    for ods in sorted(df[id_lvl].unique()):
        datos_ods = df[df[id_lvl] == ods][score]
        
        fig.add_trace(go.Violin(
            y=datos_ods,
            name=f'ODS {ods}',
            box_visible=True,
            meanline_visible=True,
            fillcolor=px.colors.qualitative.Plotly[int(ods) % len(px.colors.qualitative.Plotly)],
            opacity=0.6,
            x0=f'ODS {ods}'
        ))
    
    fig.update_layout(
        title='Violin Plot: Distribución de Densidad de Similaridad por ODS<br><sub>Análisis detallado de concentración de valores</sub>',
        yaxis_title='Similaridad Coseno',
        xaxis_title='Objetivo de Desarrollo Sostenible',
        height=600,
        showlegend=False
    )
    
    return fig


# ============================================================================
# 10. GRÁFICA 9: DASHBOARD INTEGRADO - Métricas Clave
# ============================================================================

def viz_9_dashboard_metricas(df, id_lvl, score, rank, titulo):
    """
    LÓGICA: Dashboard con múltiples paneles que resume las métricas clave:
    - Panel 1: Top 10 indicadores con mayor similaridad
    - Panel 2: Estadísticas por ODS (media, std, max, min)
    - Panel 3: Distribución global de similaridad (histograma)
    - Panel 4: Correlación entre rank y similaridad
    
    INTERPRETACIÓN:
    - Vista holística de la calidad del matching
    - Permite validar que el ranking está bien correlacionado con similaridad
    - Identifica outliers o problemas en el cálculo
    - Facilita comunicación de resultados a stakeholders
    """
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Top 10 Indicadores por Similaridad',
            'Estadísticas por ODS',
            'Distribución Global de Similaridad',
            'Correlación: Rank vs Similaridad'
        ),
        specs=[
            [{"type": "bar"}, {"type": "table"}],
            [{"type": "histogram"}, {"type": "scatter"}]
        ]
    )
    
    # Panel 1: Top 10
    top_10 = df.nsmallest(10, rank)
    fig.add_trace(
        go.Bar(
            x=top_10[score],
            y=top_10['indicador_id'],
            orientation='h',
            marker_color='lightblue',
            text=top_10[score].round(4),
            textposition='auto'
        ),
        row=1, col=1
    )
    
    # Panel 2: Tabla de estadísticas
    stats_ods = df.groupby(id_lvl)[score].agg(['mean', 'std', 'min', 'max', 'count']).reset_index()
    stats_ods.columns = ['ODS', 'Media', 'Std', 'Min', 'Max', 'Count']
    stats_ods = stats_ods.round(4)
    
    fig.add_trace(
        go.Table(
            header=dict(values=list(stats_ods.columns),
                       fill_color='paleturquoise',
                       align='left'),
            cells=dict(values=[stats_ods[col] for col in stats_ods.columns],
                      fill_color='lavender',
                      align='left')
        ),
        row=1, col=2
    )
    
    # Panel 3: Histograma
    fig.add_trace(
        go.Histogram(
            x=df[score],
            nbinsx=30,
            marker_color='indianred',
            name='Distribución'
        ),
        row=2, col=1
    )
    
    # Panel 4: Scatter rank vs similaridad
    fig.add_trace(
        go.Scatter(
            x=df[rank],
            y=df[score],
            mode='markers',
            marker=dict(
                size=5,
                color=df[id_lvl],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="ODS", x=1.15)
            ),
            text=df['indicador_id']
        ),
        row=2, col=2
    )
    
    # Añadir línea de tendencia
    z = np.polyfit(df[rank], df[score], 1)
    p = np.poly1d(z)
    fig.add_trace(
        go.Scatter(
            x=df[rank],
            y=p(df[rank]),
            mode='lines',
            line=dict(color='red', dash='dash'),
            name='Tendencia'
        ),
        row=2, col=2
    )
    
    fig.update_xaxes(title_text="Similaridad", row=1, col=1)
    fig.update_xaxes(title_text="Similaridad", row=2, col=1)
    fig.update_xaxes(title_text="Rank", row=2, col=2)
    fig.update_yaxes(title_text="Indicador", row=1, col=1)
    fig.update_yaxes(title_text="Frecuencia", row=2, col=1)
    fig.update_yaxes(title_text="Similaridad", row=2, col=2)
    
    fig.update_layout(
        height=900,
        showlegend=False,
        title_text="Dashboard Integrado: Métricas Clave de Similaridad ODS",
        title_x=0.5
    )
    
    return fig


# ============================================================================
# 11. GRÁFICA 10: MATRIZ DE TRANSICIÓN - Cambios de ODS por Ranking
# ============================================================================

def viz_10_matriz_transicion(df, id_lvl, score, rank, titulo):
    """
    LÓGICA: Muestra cómo cambia el ODS dominante a medida que avanzamos
    en el ranking. Divide el ranking en cuartiles y muestra qué ODS
    tiene más presencia en cada cuartil.
    
    INTERPRETACIÓN:
    - Permite ver si un ODS domina consistentemente
    - Identifica cambios de dominancia (ej: ODS 5 domina top rankings,
      luego ODS 17)
    - Útil para entender si la iniciativa es más afín a ciertos ODS
    - Ayuda a explicar por qué ciertos ODS aparecen más arriba
    """
    
    # Crear cuartiles
    df['cuartil'] = pd.qcut(df[rank], q=4, labels=['Q1 (Top)', 'Q2', 'Q3', 'Q4 (Bottom)'])
    
    # Contar presencia de ODS por cuartil
    matriz = pd.crosstab(df[id_lvl], df['cuartil'], normalize='columns') * 100
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    sns.heatmap(
        matriz,
        annot=True,
        fmt='.1f',
        cmap='YlOrRd',
        cbar_kws={'label': '% de Presencia en Cuartil'},
        linewidths=0.5,
        ax=ax
    )
    
    ax.set_title(
        'Matriz de Transición: Presencia de ODS por Cuartil de Ranking\n'
        'Análisis de dominancia y evolución',
        fontsize=14,
        pad=20
    )
    ax.set_xlabel('Cuartil de Ranking', fontsize=12)
    ax.set_ylabel('ODS ID', fontsize=12)
    
    plt.tight_layout()
    return fig


# ============================================================================
# 12. FUNCIÓN PRINCIPAL - GENERAR TODAS LAS VISUALIZACIONES
# ============================================================================

def generar_todas_visualizaciones(ruta_archivo, guardar=True, formato='html'):
    """
    Función principal que genera todas las visualizaciones.
    
    Parámetros:
    -----------
    ruta_archivo : str
        Ruta al archivo markdown con los datos
    guardar : bool
        Si True, guarda las visualizaciones en archivos
    formato : str
        Formato de salida: 'html' para interactivas, 'png' para estáticas
    
    Retorna:
    --------
    dict : Diccionario con todas las figuras generadas
    """
    
    print("Cargando datos...")
    df = cargar_datos(ruta_archivo)
    print(f"Datos cargados: {len(df)} registros, {df[id_lvl].nunique()} ODS únicos")
    
    figuras = {}
    
    print("\n" + "="*70)
    print("GENERANDO VISUALIZACIONES")
    print("="*70)
    
    # Visualización 1
    print("\n[1/10] Generando distribución por ODS (Box Plot)...")
    figuras['viz1_boxplot'] = viz_1_distribucion_por_ods(df)
    if guardar:
        figuras['viz1_boxplot'].write_html('viz1_boxplot_ods.html')
    
    # Visualización 2
    print("[2/10] Generando heatmap ODS vs Ranking...")
    figuras['viz2_heatmap'] = viz_2_heatmap_ods_ranking(df)
    if guardar:
        figuras['viz2_heatmap'].savefig('viz2_heatmap.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    # Visualización 3
    print("[3/10] Generando scatter 3D interactivo...")
    figuras['viz3_scatter3d'] = viz_3_scatter_3d_interactivo(df)
    if guardar:
        figuras['viz3_scatter3d'].write_html('viz3_scatter3d.html')
    
    # Visualización 4
    print("[4/10] Generando radar chart por ODS...")
    figuras['viz4_radar'] = viz_4_radar_chart_ods(df)
    if guardar:
        figuras['viz4_radar'].write_html('viz4_radar_ods.html')
    
    # Visualización 5
    print("[5/10] Generando sunburst jerárquico...")
    figuras['viz5_sunburst'] = viz_5_sunburst_jerarquia(df)
    if guardar:
        figuras['viz5_sunburst'].write_html('viz5_sunburst.html')
    
    # Visualización 6
    print("[6/10] Generando top indicadores por ODS...")
    figuras['viz6_topn'] = viz_6_top_indicadores_por_ods(df, top_n=5)
    if guardar:
        figuras['viz6_topn'].write_html('viz6_top_indicadores.html')
    
    # Visualización 7
    print("[7/10] Generando stream graph...")
    figuras['viz7_stream'] = viz_7_streamgraph_similaridad(df)
    if guardar:
        figuras['viz7_stream'].write_html('viz7_streamgraph.html')
    
    # Visualización 8
    print("[8/10] Generando violin plot...")
    figuras['viz8_violin'] = viz_8_violin_plot_ods(df)
    if guardar:
        figuras['viz8_violin'].write_html('viz8_violin_plot.html')
    
    # Visualización 9
    print("[9/10] Generando dashboard integrado...")
    figuras['viz9_dashboard'] = viz_9_dashboard_metricas(df)
    if guardar:
        figuras['viz9_dashboard'].write_html('viz9_dashboard.html')
    
    # Visualización 10
    print("[10/10] Generando matriz de transición...")
    figuras['viz10_matriz'] = viz_10_matriz_transicion(df)
    if guardar:
        figuras['viz10_matriz'].savefig('viz10_matriz_transicion.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print("\n" + "="*70)
    print("GENERACIÓN COMPLETADA")
    print("="*70)
    print(f"\nTotal de visualizaciones generadas: {len(figuras)}")
    
    if guardar:
        print("\nArchivos guardados:")
        print("  - Visualizaciones interactivas (HTML): 8 archivos")
        print("  - Visualizaciones estáticas (PNG): 2 archivos")
    
    return figuras, df


# ============================================================================
# 13. ANÁLISIS ESTADÍSTICO COMPLEMENTARIO
# ============================================================================

def analisis_estadistico(df):
    """
    Genera estadísticas descriptivas complementarias para el análisis
    """
    print("\n" + "="*70)
    print("ANÁLISIS ESTADÍSTICO COMPLEMENTARIO")
    print("="*70)
    
    print("\n1. ESTADÍSTICAS GLOBALES")
    print("-" * 70)
    print(f"   Similaridad media: {df[score].mean():.4f}")
    print(f"   Desviación estándar: {df[score].std():.4f}")
    print(f"   Similaridad mínima: {df[score].min():.4f}")
    print(f"   Similaridad máxima: {df[score].max():.4f}")
    print(f"   Mediana: {df[score].median():.4f}")
    
    print("\n2. ESTADÍSTICAS POR ODS")
    print("-" * 70)
    stats_ods = df.groupby(id_lvl)[score].agg([
        ('count', 'count'),
        ('mean', 'mean'),
        ('std', 'std'),
        ('min', 'min'),
        ('max', 'max')
    ]).round(4)
    print(stats_ods.to_string())
    
    print("\n3. ODS MÁS REPRESENTADOS EN TOP 50")
    print("-" * 70)
    top_50_ods = df.nsmallest(50, rank)[id_lvl].value_counts()
    print(top_50_ods.to_string())
    
    print("\n4. CORRELACIÓN RANK vs SIMILARIDAD")
    print("-" * 70)
    correlacion = df[rank].corr(df[score])
    print(f"   Correlación de Pearson: {correlacion:.4f}")
    print(f"   Interpretación: {'Negativa fuerte' if correlacion < -0.7 else 'Negativa moderada' if correlacion < -0.4 else 'Negativa débil'}")
    print(f"   (Esperado: correlación negativa, a mayor rank → menor similaridad)")
    
    return stats_ods


# ============================================================================
# EJECUCIÓN DEL SCRIPT
# ============================================================================

if __name__ == "__main__":
    # Configurar ruta del archivo
    RUTA_ARCHIVO = '/mnt/user-data/uploads/indicadores_markdown.txt'
    
    print("\n" + "="*70)
    print("SISTEMA DE VISUALIZACIÓN - ANÁLISIS DE SIMILARIDAD ODS")
    print("="*70)
    print("\nEste script genera 10 visualizaciones avanzadas para analizar")
    print("la similaridad coseno como proxy de relevancia entre una iniciativa")
    print("ciudadana y los indicadores ODS.")
    
    # Generar todas las visualizaciones
    figuras, df = generar_todas_visualizaciones(
        RUTA_ARCHIVO,
        guardar=True,
        formato='html'
    )
    
    # Análisis estadístico
    stats = analisis_estadistico(df)
    
    print("\n" + "="*70)
    print("RECOMENDACIONES DE USO")
    print("="*70)
    print("""
    1. Use el Dashboard (viz9) como punto de partida para exploración general
    2. Use el Heatmap (viz2) para identificar patrones temporales de relevancia
    3. Use el Radar Chart (viz4) para comunicar el perfil ODS de la iniciativa
    4. Use el Scatter 3D (viz3) para exploración detallada e interactiva
    5. Use el Violin Plot (viz8) para análisis estadístico profundo
    6. Use el Sunburst (viz5) para presentaciones ejecutivas
    7. Use la Matriz de Transición (viz10) para análisis de consistencia
    
    NOTA: Los archivos HTML son interactivos - ábralos en un navegador
    """)
    
    print("\n¡Proceso completado exitosamente!")
