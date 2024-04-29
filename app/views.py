from flask import render_template, request, Response
from .utils import cargar_datos
import locale
import pandas as pd

# Establece la configuración regional para que las fechas se muestren en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def formatear_fecha(fecha):
    if pd.isnull(fecha):  # Comprueba si la fecha es NaT/NaN
        return "No disponible"
    return fecha.strftime('%d de %B de %Y')

def init_views(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            reset = request.form.get('reset')
            if reset == 'true':
                df = cargar_datos()
                # Asegúrate de que pandas interprete la columna de lanzamiento como una fecha
                df['inicio'] = pd.to_datetime(df['inicio'], errors='coerce')

                # Formatea cada fecha de lanzamiento en el DataFrame
                df['inicio'] = df['inicio'].apply(formatear_fecha)

                # Obtener lista de dominios únicos
                dominios = df['dominio'].dropna().unique().tolist()
                
                productos = df[['producto', 'org', 'inicio', 'precio', 'dominio']].to_dict('records')

                return render_template('index.html', productos=productos, dominios=dominios)

        # Si no es una solicitud POST o no es un restablecimiento, procede normalmente
        df = cargar_datos()
        # Asegúrate de que pandas interprete la columna de lanzamiento como una fecha
        df['inicio'] = pd.to_datetime(df['inicio'], errors='coerce')

        # Formatea cada fecha de lanzamiento en el DataFrame
        df['inicio'] = df['inicio'].apply(formatear_fecha)

        # Obtener lista de dominios únicos
        dominios = df['dominio'].dropna().unique().tolist()
        
        productos = df[['producto', 'org', 'inicio', 'precio', 'dominio']].to_dict('records')

        # Filtrar por dominio si es seleccionado
        selected_dominios = request.form.getlist('dominio')
        if selected_dominios:  # Si se seleccionan dominios, mostrar solo los productos asociados
            productos = [p for p in productos if p['dominio'] in selected_dominios]

        return render_template('index.html', productos=productos, dominios=dominios, selected_dominios=selected_dominios)