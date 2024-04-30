from flask import render_template, request
from .utils import cargar_datos
import locale
import pandas as pd

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def formatear_fecha(fecha):
    return "No disponible" if pd.isnull(fecha) else fecha.strftime('%d de %B de %Y')

def init_views(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        df = cargar_datos()
        df['inicio'] = pd.to_datetime(df['inicio'], errors='coerce')
        df['inicio'] = df['inicio'].apply(formatear_fecha)

        dominios = df['dominio'].dropna().unique().tolist()
        tipos = df['tipo'].dropna().unique().tolist()

        if request.method == 'POST':
            if request.form.get('reset') == 'true':
                productos = df[['producto', 'org', 'inicio', 'precio', 'dominio', 'tipo']].to_dict('records')
                return render_template('index.html', productos=productos, dominios=dominios, tipos=tipos)

            selected_dominios = request.form.getlist('dominio')
            selected_tipos = request.form.getlist('tipo')

            if selected_dominios:
                df = df[df['dominio'].isin(selected_dominios)]
            if selected_tipos:
                df = df[df['tipo'].isin(selected_tipos)]

            productos = df[['producto', 'org', 'inicio', 'precio', 'dominio', 'tipo']].to_dict('records')
            return render_template('index.html', productos=productos, dominios=dominios, tipos=tipos, selected_dominios=selected_dominios, selected_tipos=selected_tipos)

        productos = df[['producto', 'org', 'inicio', 'precio', 'dominio', 'tipo']].to_dict('records')
        return render_template('index.html', productos=productos, dominios=dominios, tipos=tipos)
