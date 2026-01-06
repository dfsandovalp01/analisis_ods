# 🚀 Aplicación Web Gradio - Visualizaciones ODS

## 📋 Descripción

**App Gradio Interactiva** para explorar las 10 visualizaciones de análisis de similaridad ODS a través de una interfaz web profesional y amigable.

### ✨ Características Principales

- ✅ **Interfaz web interactiva** con diseño profesional
- ✅ **10 pestañas** con cada visualización completa
- ✅ **Explicaciones integradas** para público general
- ✅ **Visualizaciones dinámicas** (Plotly) y estáticas (PNG)
- ✅ **Estadísticas en tiempo real** con análisis detallado
- ✅ **Dashboard de inicio** con métricas clave
- ✅ **Responsive design** adaptable a cualquier pantalla
- ✅ **Sin necesidad de conocimientos técnicos** para usar

---

## 🎯 ¿Para quién es esta aplicación?

### 👥 Público General
- Explorar visualizaciones de forma intuitiva
- Entender qué ODS son más relevantes
- Identificar indicadores clave sin código

### 👔 Ejecutivos y Tomadores de Decisión
- Presentaciones interactivas
- Análisis rápido de alineación ODS
- Métricas clave de un vistazo

### 🔬 Analistas e Investigadores
- Exploración profunda de datos
- Validación de correlaciones
- Exportación de visualizaciones

### 👨‍💻 Desarrolladores
- Referencia de implementación
- Base para personalización
- Integración con otros sistemas

---

## 🛠️ Instalación y Configuración

### Requisitos Previos

```bash
# Python 3.8 o superior
python --version

# Librerías necesarias
pip install pandas numpy matplotlib seaborn plotly gradio
```

### Instalación Completa

```bash
# 1. Instalar todas las dependencias
pip install pandas numpy matplotlib seaborn plotly gradio --break-system-packages

# 2. Verificar instalación
python -c "import gradio; print(f'Gradio {gradio.__version__} instalado correctamente')"
```

---

## 🚀 Ejecución de la Aplicación

### Método 1: Ejecución Directa

```bash
# Navegar al directorio
cd /ruta/donde/está/app_gradio_ods.py

# Ejecutar la aplicación
python app_gradio_ods.py
```

**Resultado esperado:**
```
======================================================================
INICIANDO APLICACIÓN GRADIO - VISUALIZACIONES ODS
======================================================================

✓ Datos cargados correctamente: 244 registros
✓ ODS únicos: 17

======================================================================
CREANDO APLICACIÓN...
======================================================================

✓ Aplicación creada exitosamente

======================================================================
INICIANDO SERVIDOR WEB...
======================================================================

🌐 La aplicación se abrirá en tu navegador automáticamente
📍 URL local: http://127.0.0.1:7860
🌍 URL pública: Se generará si share=True

💡 Presiona Ctrl+C para detener el servidor

Running on local URL:  http://127.0.0.1:7860
```

### Método 2: Ejecución en Background

```bash
# Para mantener la app corriendo en segundo plano
nohup python app_gradio_ods.py > app.log 2>&1 &

# Ver los logs
tail -f app.log

# Detener la aplicación
pkill -f app_gradio_ods.py
```

### Método 3: Compartir Públicamente

Editar el archivo `app_gradio_ods.py` en la línea final:

```python
# Cambiar de:
app.launch(share=False)

# A:
app.launch(share=True)
```

Esto generará una URL pública accesible desde cualquier lugar por 72 horas.

---

## 📱 Uso de la Aplicación

### Pantalla de Inicio

Al abrir la aplicación, verás:

1. **Título principal** con descripción
2. **Estadísticas generales** en tarjeta destacada
3. **Top 3 ODS** más relevantes
4. **Top 5 indicadores** en tabla
5. **Guía de uso** paso a paso

### Navegación por Pestañas

#### 🏠 **Inicio**
- Dashboard con resumen ejecutivo
- Métricas clave del análisis
- Recomendaciones de exploración

#### 📦 **1. Box Plot**
- Distribución de similaridad por ODS
- Clic en "🔄 Generar Visualización"
- Explicación a la derecha
- Gráfico interactivo a la izquierda

#### 🔥 **2. Heatmap**
- Mapa de calor ODS × Ranking
- Imagen estática de alta resolución
- Interpretación de colores

#### 🌐 **3. Scatter 3D**
- Exploración tridimensional
- **Rotar**: Arrastra con el mouse
- **Zoom**: Scroll o rueda del mouse
- **Hover**: Ver detalles de cada punto

#### 🕸️ **4. Radar Chart**
- Perfil circular de ODS
- Dos polígonos superpuestos
- Ideal para presentaciones

#### ☀️ **5. Sunburst**
- Jerarquía ODS → Indicadores
- **Clic**: Zoom en segmento
- Tamaño proporcional a similaridad

#### 🏆 **6. Top Indicadores**
- Top 5 por cada ODS
- 17 paneles (uno por ODS)
- Scroll vertical para explorar todos

#### 🌊 **7. Stream Graph**
- Evolución de contribución
- Áreas apiladas al 100%
- Cambios de dominancia

#### 🎻 **8. Violin Plot**
- Distribución detallada
- Densidad de probabilidad
- Detecta patrones complejos

#### 📊 **9. Dashboard**
- 4 paneles integrados
- Vista 360° del análisis
- Validación del sistema

#### 🔀 **10. Matriz Transición**
- Presencia por cuartiles
- Consistencia de ODS
- Análisis de dominancia

#### 📈 **Estadísticas**
- Análisis estadístico completo
- Tablas detalladas por ODS
- Validación de correlaciones

---

## 🎨 Personalización

### Cambiar Colores

Editar en `app_gradio_ods.py`:

```python
# Línea ~35 - Tema de colores
theme=gr.themes.Soft(
    primary_hue="blue",      # Cambiar a: "green", "red", "purple", etc.
    secondary_hue="cyan",    # Cambiar a: "teal", "orange", "pink", etc.
    neutral_hue="slate"      # Cambiar a: "gray", "zinc", "stone", etc.
)
```

### Cambiar Puerto

```python
# Línea final - Configuración del servidor
app.launch(
    server_port=7860,  # Cambiar a: 8000, 8080, 3000, etc.
)
```

### Agregar Autenticación

```python
# Línea final - Añadir usuario/contraseña
app.launch(
    auth=("usuario", "contraseña"),  # Credenciales de acceso
    auth_message="Ingrese sus credenciales para acceder"
)
```

### Modificar Explicaciones

Editar las funciones `tab_vizN()` en el archivo:

```python
def tab_viz1():
    # ...
    explicacion = """
    ## Tu título personalizado
    
    Tu texto explicativo aquí...
    """
    # ...
```

---

## 🔧 Solución de Problemas

### Problema 1: "ModuleNotFoundError: No module named 'gradio'"

**Solución:**
```bash
pip install gradio --break-system-packages
```

### Problema 2: "Address already in use"

**Causa:** El puerto 7860 ya está siendo usado

**Solución A - Cambiar puerto:**
```python
app.launch(server_port=8080)  # Usar otro puerto
```

**Solución B - Cerrar proceso existente:**
```bash
lsof -ti:7860 | xargs kill -9
```

### Problema 3: "⚠️ Error: No se pudieron cargar los datos"

**Causa:** Ruta incorrecta del archivo de datos

**Solución:**
```python
# Editar línea ~49 en app_gradio_ods.py
RUTA_DATOS = '/ruta/correcta/a/indicadores_markdown.txt'
```

### Problema 4: Las visualizaciones no se cargan

**Causa:** Falta el archivo `visualizaciones_ods.py`

**Solución:**
```bash
# Asegurarse de tener ambos archivos en el mismo directorio
ls -la app_gradio_ods.py visualizaciones_ods.py
```

### Problema 5: Error de memoria con muchos datos

**Solución - Limitar datos:**
```python
# Editar en cargar_datos()
df = df.sample(n=1000)  # Muestra de 1000 registros
```

### Problema 6: La app no se abre automáticamente

**Solución:**
```bash
# Abrir manualmente en navegador
google-chrome http://127.0.0.1:7860  # Chrome
firefox http://127.0.0.1:7860        # Firefox
open http://127.0.0.1:7860           # macOS
```

---

## 📊 Capturas de Pantalla

### Vista del Dashboard de Inicio
```
┌─────────────────────────────────────────────────────┐
│  📊 Sistema de Visualización ODS                     │
│  Análisis de Similaridad de Indicadores             │
│                                                      │
│  📈 Estadísticas Generales                           │
│  ┌──────────────────────────────────────────────┐   │
│  │ Total indicadores: 244                       │   │
│  │ ODS cubiertos: 17/17 (100%)                  │   │
│  │ Similaridad promedio: 0.9050                 │   │
│  │ Correlación: -0.9837 ✅                       │   │
│  └──────────────────────────────────────────────┘   │
│                                                      │
│  🏆 Top 3 ODS Más Relevantes                        │
│  1. ODS 17: 0.9223                                  │
│  2. ODS 16: 0.9183                                  │
│  3. ODS 9: 0.9199                                   │
└─────────────────────────────────────────────────────┘
```

### Vista de Visualización Individual
```
┌─────────────────────────────────────────────────────┐
│  [Pestaña]  📦 1. Box Plot                          │
├─────────────────────┬───────────────────────────────┤
│                     │  ## 📦 Diagrama de Caja      │
│   [Gráfico          │                               │
│    Interactivo      │  ### ¿Qué muestra?           │
│    Plotly]          │  Esta visualización...        │
│                     │                               │
│                     │  ### ¿Cómo leerlo?           │
│                     │  - Línea central: Mediana    │
│  [🔄 Generar]       │  - Caja: Rango IQR           │
└─────────────────────┴───────────────────────────────┘
```

---

## 🌐 Compartir y Colaborar

### Opción 1: Compartir en Red Local

```python
# Permite acceso desde otras computadoras en la misma red
app.launch(
    server_name="0.0.0.0",  # Ya está configurado por defecto
)
```

**Acceso desde otra computadora:**
```
http://[IP-DEL-SERVIDOR]:7860
```

### Opción 2: Compartir Públicamente (72 horas)

```python
app.launch(share=True)
```

**Resultado:**
```
Running on local URL:  http://127.0.0.1:7860
Running on public URL: https://abc123xyz.gradio.live

This share link expires in 72 hours.
```

### Opción 3: Deployar en la Nube

#### **Hugging Face Spaces** (Gratis)

1. Crear cuenta en huggingface.co
2. Crear nuevo Space
3. Subir archivos:
   - `app_gradio_ods.py`
   - `visualizaciones_ods.py`
   - `indicadores_markdown.txt`
   - `requirements.txt`

**requirements.txt:**
```
gradio==5.49.1
pandas
numpy
matplotlib
seaborn
plotly
```

4. Tu app estará en: `https://huggingface.co/spaces/[tu-usuario]/[nombre-app]`

---

## 📚 Estructura de Archivos

```
proyecto/
│
├── app_gradio_ods.py              # ⭐ Aplicación principal
├── visualizaciones_ods.py         # Funciones de visualización
├── indicadores_markdown.txt        # Datos de entrada
│
├── GUIA_APP_GRADIO.md             # 📖 Esta guía
├── README.md                       # Índice general
│
└── outputs/                        # Visualizaciones generadas
    ├── viz1_boxplot_ods.html
    ├── viz2_heatmap.png
    └── ...
```

---

## 🎓 Casos de Uso Avanzados

### Caso 1: Integrar con otros datos

```python
# En app_gradio_ods.py, añadir nuevo tab
with gr.Tab("📁 Cargar Datos"):
    file_upload = gr.File(label="Subir archivo CSV/TXT")
    btn_load = gr.Button("Cargar")
    
    def cargar_nuevos_datos(file):
        df = pd.read_csv(file.name)
        # Procesar y visualizar
        return "✓ Datos cargados"
    
    btn_load.click(cargar_nuevos_datos, file_upload, output_text)
```

### Caso 2: Exportar visualizaciones

```python
# Añadir botones de descarga
with gr.Row():
    btn_download_html = gr.Button("📥 Descargar HTML")
    btn_download_png = gr.Button("📥 Descargar PNG")

def exportar_viz(fig, formato):
    if formato == "html":
        fig.write_html("visualizacion.html")
        return "visualizacion.html"
    else:
        fig.write_image("visualizacion.png")
        return "visualizacion.png"
```

### Caso 3: Filtros dinámicos

```python
# Añadir controles interactivos
with gr.Row():
    ods_select = gr.Dropdown(
        choices=list(range(1, 18)),
        label="Filtrar por ODS",
        multiselect=True
    )
    slider_sim = gr.Slider(
        minimum=0.85,
        maximum=0.95,
        value=0.90,
        label="Umbral de similaridad"
    )

def filtrar_datos(ods_list, umbral):
    df_filtrado = df_global[
        (df_global['ods_id'].isin(ods_list)) & 
        (df_global['similaridad_cos'] >= umbral)
    ]
    return generar_visualizacion(df_filtrado)
```

---

## 🔐 Seguridad y Buenas Prácticas

### Recomendaciones

1. ✅ **No exponer datos sensibles** en la app pública
2. ✅ **Usar autenticación** si compartes públicamente
3. ✅ **Limitar acceso** a redes confiables
4. ✅ **Validar inputs** del usuario
5. ✅ **Mantener actualizado** Gradio y dependencias

### Autenticación Básica

```python
app.launch(
    auth=[("usuario1", "pass1"), ("usuario2", "pass2")],
    auth_message="Acceso restringido - Ingrese credenciales"
)
```

### Variables de Entorno

```python
import os

# Usar variables de entorno para credenciales
usuario = os.getenv("APP_USERNAME", "admin")
password = os.getenv("APP_PASSWORD", "secret")

app.launch(auth=(usuario, password))
```

---

## 📞 Soporte y Recursos

### Documentación Oficial
- **Gradio**: https://www.gradio.app/docs
- **Plotly**: https://plotly.com/python/
- **Pandas**: https://pandas.pydata.org/docs/

### Comunidad
- **Gradio Discord**: https://discord.gg/gradio
- **Hugging Face Forums**: https://discuss.huggingface.co/

### Archivos Relacionados
- `README.md` - Índice general del proyecto
- `GUIA_VISUALIZACIONES_ODS.md` - Explicación de visualizaciones
- `DOCUMENTACION_TECNICA_CODIGO.md` - Código técnico explicado
- `GUIA_USO_RAPIDO.md` - Casos prácticos

---

## 🎉 Características Futuras (Roadmap)

### En Desarrollo
- [ ] Comparación de múltiples iniciativas
- [ ] Exportación de reportes en PDF
- [ ] Análisis de series temporales
- [ ] Integración con APIs de ODS oficiales

### Planeado
- [ ] Modo oscuro / claro
- [ ] Internacionalización (ES, EN, FR)
- [ ] Chat con IA para interpretación
- [ ] Dashboard personalizable

---

## 📄 Licencia

Este proyecto es de código abierto. Consulta el archivo LICENSE para más detalles.

---

## 🙏 Agradecimientos

Desarrollado con:
- **Python** - Lenguaje de programación
- **Gradio** - Framework de aplicaciones web
- **Plotly** - Visualizaciones interactivas
- **Pandas** - Análisis de datos
- **Matplotlib/Seaborn** - Gráficos estáticos

---

## 📬 Contacto

¿Preguntas? ¿Sugerencias? ¿Encontraste un bug?

- 📧 Email: [tu-email@ejemplo.com]
- 💬 Issues: [URL del repositorio]
- 📖 Wiki: [URL de la wiki]

---

**¡Disfruta explorando las visualizaciones ODS! 📊🌍✨**

---

*Última actualización: Noviembre 2025*
