from flask import render_template, request
from .models import Index
from .database import db
import locale
from sqlalchemy import and_
from .utildate import extract_fecha_dinamica

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def formatear_fecha(fecha):
    if fecha is None:
        return "No disponible"
    return fecha.strftime('%d de %B de %Y')

def init_views(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        # Llamada directa a la función que obtiene la fecha dinámicamente
        fecha_version = extract_fecha_dinamica()

        # Cargar opciones de filtro independientemente de los productos
        dominios, tipos, orgs, price_ranges = load_filter_options()

        query = db.session.query(Index)
        # Recoger valores de formulario
        selected_dominios = request.form.getlist('dominio')
        selected_tipos = request.form.getlist('tipo')
        selected_orgs = request.form.getlist('org')
        selected_price_range = request.form.get('price_range')

        if request.method == 'POST':
            if request.form.get('reset') == 'true':
                # Si es reset, no aplicar filtros
                productos = query.all()
            else:
                # Aplicar filtros
                if selected_dominios:
                    query = query.filter(Index.dominio.in_(selected_dominios))
                if selected_tipos:
                    query = query.filter(Index.tipo.in_(selected_tipos))
                if selected_orgs:
                    query = query.filter(Index.org.in_(selected_orgs))
                if selected_price_range:
                    if selected_price_range == "Menos de S/. 500":
                        query = query.filter(Index.m_soles < 500)
                    elif selected_price_range == "S/. 500 a S/. 1,000":
                        query = query.filter(and_(Index.m_soles >= 500, Index.m_soles <= 1000))
                    elif selected_price_range == "S/. 1,000 a S/. 1,500":
                        query = query.filter(and_(Index.m_soles >= 1000, Index.m_soles <= 1500))
                    elif selected_price_range == "S/. 1,500 a S/. 2,500":
                        query = query.filter(and_(Index.m_soles >= 1500, Index.m_soles <= 2500))
                    elif selected_price_range == "S/. 2,500 a S/. 4,000":
                        query = query.filter(and_(Index.m_soles >= 2500, Index.m_soles <= 4000))
                    elif selected_price_range == "Más de S/. 4,000":
                        query = query.filter(Index.m_soles > 4000)
                productos = query.all()
        else:
            # Carga inicial sin filtros
            productos = query.all()

        productos = [{
            'producto': prod.producto,
            'org': prod.org,
            'inicio': formatear_fecha(prod.inicio),
            'precio': prod.precio,
            'm_soles': prod.m_soles,
            'dominio': prod.dominio,
            'tipo': prod.tipo,
            'url_especf': prod.url_especf
        } for prod in productos]

        return render_template('index.html', productos=productos, dominios=dominios, tipos=tipos, orgs=orgs, price_ranges=price_ranges,
                               selected_dominios=selected_dominios, selected_tipos=selected_tipos, selected_orgs=selected_orgs, selected_price_range=selected_price_range, fecha_version=fecha_version)


    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error404.html'), 404

def load_filter_options():
    dominios = [dominio[0] for dominio in db.session.query(Index.dominio).distinct().all()]
    tipos = [tipo[0] for tipo in db.session.query(Index.tipo).distinct().all()]
    orgs = [org[0] for org in db.session.query(Index.org).distinct().all()]
    price_ranges = [
        "Menos de S/. 500",
        "S/. 500 a S/. 1,000",
        "S/. 1,000 a S/. 1,500",
        "S/. 1,500 a S/. 2,500",
        "S/. 2,500 a S/. 4,000",
        "Más de S/. 4,000"
    ]
    return dominios, tipos, orgs, price_ranges
