from .utils import cargar_datos
import locale
from flask import render_template
from datetime import datetime
import pandas as pd

# Establece la configuración regional para que las fechas se muestren en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def formatear_fecha(fecha):
    if pd.isnull(fecha):  # Comprueba si la fecha es NaT/NaN
        return "No disponible"
    return fecha.strftime('%d de %B de %Y')

def init_views(app):
    @app.route('/')
    def index():
        df = cargar_datos()
        # Asegúrate de que pandas interprete la columna de lanzamiento como una fecha
        df['inicio'] = pd.to_datetime(df['inicio'], errors='coerce')

        # Formatea cada fecha de lanzamiento en el DataFrame
        df['inicio'] = df['inicio'].apply(formatear_fecha)

        productos = df[['producto', 'org', 'inicio']].to_dict('records')
        return render_template('index.html', productos=productos)
