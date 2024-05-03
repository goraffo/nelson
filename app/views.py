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
        df['m_soles'] = pd.to_numeric(df['m_soles'], errors='coerce')

        dominios = df['dominio'].dropna().unique().tolist()
        tipos = df['tipo'].dropna().unique().tolist()
        orgs = df['org'].dropna().unique().tolist()
        price_ranges = [
            "Menos de S/. 500",
            "S/. 500 a S/. 1,000",
            "S/. 1,000 a S/. 1,500",
            "S/. 1,500 a S/. 2,500",
            "S/. 2,500 a S/. 4,000",
            "Más de S/. 4,000"
        ]

        # Inicializa productos aquí para asegurarse de que siempre está definido
        productos = df[['producto', 'org', 'inicio', 'precio', 'm_soles', 'dominio', 'tipo', 'url_especf']].to_dict('records')

        selected_dominios = request.form.getlist('dominio') if request.method == 'POST' else []
        selected_tipos = request.form.getlist('tipo') if request.method == 'POST' else []
        selected_orgs = request.form.getlist('org')
        selected_price_range = request.form.get('price_range') if request.method == 'POST' else ""

        if request.method == 'POST':
            if request.form.get('reset') == 'true':
                return render_template('index.html', productos=productos, dominios=dominios, tipos=tipos, price_ranges=price_ranges, selected_dominios=[], selected_tipos=[], selected_price_range="")

            if selected_dominios:
                df = df[df['dominio'].isin(selected_dominios)]
            if selected_tipos:
                df = df[df['tipo'].isin(selected_tipos)]
            if selected_orgs:
                df = df[df['org'].isin(selected_orgs)] 
            if selected_price_range:
                price_range_filters = {
                    "Menos de S/. 500": lambda x: x[x['m_soles'] < 500],
                    "S/. 500 a S/. 1,000": lambda x: x[(x['m_soles'] >= 500) & (x['m_soles'] <= 1000)],
                    "S/. 1,000 a S/. 1,500": lambda x: x[(x['m_soles'] >= 1000) & (x['m_soles'] <= 1500)],
                    "S/. 1,500 a S/. 2,500": lambda x: x[(x['m_soles'] >= 1500) & (x['m_soles'] <= 2500)],
                    "S/. 2,500 a S/. 4,000": lambda x: x[(x['m_soles'] >= 2500) & (x['m_soles'] <= 4000)],
                    "Más de S/. 4,000": lambda x: x[(x['m_soles'] > 4000)]
                }
                df = price_range_filters[selected_price_range](df)

            productos = df[['producto', 'org', 'inicio', 'precio', 'm_soles', 'dominio', 'tipo', 'url_especf']].to_dict('records')

        return render_template('index.html', productos=productos, dominios=dominios, tipos=tipos, orgs=orgs, price_ranges=price_ranges, selected_dominios=selected_dominios, selected_tipos=selected_tipos, selected_orgs=selected_orgs, selected_price_range=selected_price_range)
    
    # Manejador de error 404
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error404.html'), 404
    

