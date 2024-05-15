from flask import render_template, request, jsonify
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

        # Recoger valores de formulario
        selected_dominios = request.form.getlist('dominio')
        selected_tipos = request.form.getlist('tipo')
        selected_orgs = request.form.getlist('org')
        selected_price_range = request.form.get('price_range')

        query = db.session.query(Index)

        # Aplicar filtros
        query = apply_filters(query, selected_dominios, selected_tipos, selected_orgs, selected_price_range)

        # Cargar opciones de filtro con la consulta filtrada
        dominios, tipos, orgs, price_ranges = load_filter_options(query)

        # Carga inicial limitada de productos
        productos = query.limit(10).all()

        productos = format_product_list(productos)

        return render_template('index.html', productos=productos, dominios=dominios, tipos=tipos, orgs=orgs, price_ranges=price_ranges,
                            selected_dominios=selected_dominios, selected_tipos=selected_tipos, selected_orgs=selected_orgs, selected_price_range=selected_price_range, fecha_version=fecha_version)


    @app.route('/load-more-products', methods=['GET'])
    def load_more_products():
        offset = int(request.args.get('offset', 0))
        limit = 10  # Define cuántos productos cargar por solicitud

        # Recuperar los parámetros de filtro desde los argumentos de la solicitud
        selected_dominios = request.args.get('dominio').split(',') if request.args.get('dominio') else []
        selected_tipos = request.args.get('tipo').split(',') if request.args.get('tipo') else []
        selected_orgs = request.args.get('org').split(',') if request.args.get('org') else []
        selected_price_range = request.args.get('price_range', '')

        query = db.session.query(Index)

        # Aplicar los mismos filtros que en la carga inicial
        query = apply_filters(query, selected_dominios, selected_tipos, selected_orgs, selected_price_range)

        productos = query.offset(offset).limit(limit).all()

        productos_json = format_product_list(productos)

        # Devolver la respuesta JSON
        return jsonify(productos_json)





    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error404.html'), 404

def load_filter_options(query):
    # Obtener dominios y sus conteos (usando id_impresion)
    dominios = query.with_entities(Index.dominio, db.func.count(Index.id_impresion)).group_by(Index.dominio).all()

    # Obtener tipos y sus conteos
    tipos = query.with_entities(Index.tipo, db.func.count(Index.id_impresion)).group_by(Index.tipo).all()

    # Obtener organizaciones y sus conteos
    orgs = query.with_entities(Index.org, db.func.count(Index.id_impresion)).group_by(Index.org).all()

    # Definir rangos de precios
    price_ranges = [
        "Menos de S/. 500",
        "S/. 500 a S/. 1,000",
        "S/. 1,000 a S/. 1,500",
        "S/. 1,500 a S/. 2,500",
        "S/. 2,500 a S/. 4,000",
        "Más de S/. 4,000"
    ]

    return dominios, tipos, orgs, price_ranges


def apply_filters(query, dominios, tipos, orgs, price_range):
    if dominios:
        query = query.filter(Index.dominio.in_(dominios))
    if tipos:
        query = query.filter(Index.tipo.in_(tipos))
    if orgs:
        query = query.filter(Index.org.in_(orgs))
    if price_range:
        # Asumiendo que ya tienes una función para manejar los rangos de precios
        query = filter_by_price_range(query, price_range)
    return query

def filter_by_price_range(query, price_range):
    if price_range == "Menos de S/. 500":
        query = query.filter(Index.m_soles < 500)
    elif price_range == "S/. 500 a S/. 1,000":
        query = query.filter(and_(Index.m_soles >= 500, Index.m_soles <= 1000))
    elif price_range == "S/. 1,000 a S/. 1,500":
        query = query.filter(and_(Index.m_soles >= 1000, Index.m_soles <= 1500))
    elif price_range == "S/. 1,500 a S/. 2,500":
        query = query.filter(and_(Index.m_soles >= 1500, Index.m_soles <= 2500))
    elif price_range == "S/. 2,500 a S/. 4,000":
        query = query.filter(and_(Index.m_soles >= 2500, Index.m_soles <= 4000))
    elif price_range == "Más de S/. 4,000":
        query = query.filter(Index.m_soles > 4000)    
    return query

def format_product_list(productos):
    return [{
        'producto': prod.producto,
        'org': prod.org,
        'inicio': formatear_fecha(prod.inicio),
        'precio': prod.precio if prod.precio is not None else "",
        'm_soles': str(prod.m_soles),  # Convertir decimales
        'dominio': prod.dominio,
        'tipo': prod.tipo,
        'url_especf': prod.url_especf
    } for prod in productos]
