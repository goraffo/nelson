from flask import render_template, request, jsonify
from .models import Index
from .database import db
from sqlalchemy import and_
from .utildate import extract_fecha_dinamica, formatear_fecha_en_espanol
import os
from .search import realizar_busqueda


def init_views(app):
    @app.route('/', methods=['GET', 'POST'])
    def index():
    # Llamada directa a la función que obtiene la fecha dinámica
        fecha_version = formatear_fecha_en_espanol(extract_fecha_dinamica())

        # Recoger valores del formulario
        selected_dominios = request.form.getlist('dominio')
        selected_tipos = request.form.getlist('tipo')
        selected_orgs = request.form.getlist('org')
        selected_price_range = request.form.get('price_range')
        search_term = request.form.get('search_term', '').strip()



        # Crear la consulta base
        query = db.session.query(Index)


        # Aplicar filtros
        query = apply_filters(query, selected_dominios, selected_tipos, selected_orgs, selected_price_range)


        # Aplicar búsqueda
        productos = realizar_busqueda(query, search_term)


        # Calcular opciones de filtro basadas en los productos filtrados
        if isinstance(productos, list):
            dominios, tipos, orgs, price_ranges = calculate_filter_options_from_list(productos)
        else:
            dominios, tipos, orgs, price_ranges = load_filter_options(query)

        # Limitar manualmente si la búsqueda devolvió una lista
        if isinstance(productos, list):
            productos = productos[:10]  # Limitar a los primeros 10 resultados


        # Formatear los productos para la plantilla
        productos = format_product_list(productos)

        ga_tracking_id = os.getenv('GA_TRACKING_ID')




        return render_template(
            'index.html',
            productos=productos,
            dominios=dominios,
            tipos=tipos,
            orgs=orgs,
            price_ranges=price_ranges,
            selected_dominios=selected_dominios,
            selected_tipos=selected_tipos,
            selected_orgs=selected_orgs,
            selected_price_range=selected_price_range,
            search_term=search_term,
            fecha_version=fecha_version,
            ga_tracking_id=ga_tracking_id
        )



    @app.route('/load-more-products', methods=['GET'])
    def load_more_products():
        offset = int(request.args.get('offset', 0))
        limit = 10  # Número de productos por solicitud

        # Recuperar los parámetros de filtro desde los argumentos de la solicitud
        selected_dominios = request.args.get('dominio', '').split(',') if request.args.get('dominio') else []
        selected_tipos = request.args.get('tipo', '').split(',') if request.args.get('tipo') else []
        selected_orgs = request.args.get('org', '').split(',') if request.args.get('org') else []
        selected_price_range = request.args.get('price_range', '')
        search_term = request.args.get('search_term', '').strip()



        # Crear la consulta base
        query = db.session.query(Index)

        # Aplicar los filtros recibidos
        query = apply_filters(query, selected_dominios, selected_tipos, selected_orgs, selected_price_range)

        # Aplicar búsqueda si hay un término
        productos = realizar_busqueda(query, search_term)

        # Manejar según sea lista o consulta SQLAlchemy
        if isinstance(productos, list):
            # Si es una lista, aplicar offset y límite manualmente
            productos = productos[offset:offset + limit]
        else:
            # Si es una consulta SQLAlchemy, usar offset y límite propios de SQL
            productos = productos.offset(offset).limit(limit).all()

        # Formatear los productos para enviarlos al frontend
        productos_json = format_product_list(productos)



        return jsonify(productos_json)



    @app.route('/terminos-y-condiciones')
    def terminos_y_condiciones():
        return render_template('terminos_y_condiciones.html')

    @app.route('/politica-privacidad')
    def politica_privacidad():
        return render_template('politica_privacidad.html')

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

    # Obtener rangos de precios y sus conteos, excluyendo los que tienen 0 productos
    price_ranges = [
        ("Menos de S/. 500", query.filter(Index.m_soles < 500).count()),
        ("S/. 500 a S/. 1,000", query.filter(and_(Index.m_soles >= 500, Index.m_soles <= 1000)).count()),
        ("S/. 1,000 a S/. 1,500", query.filter(and_(Index.m_soles >= 1000, Index.m_soles <= 1500)).count()),
        ("S/. 1,500 a S/. 2,500", query.filter(and_(Index.m_soles >= 1500, Index.m_soles <= 2500)).count()),
        ("S/. 2,500 a S/. 4,000", query.filter(and_(Index.m_soles >= 2500, Index.m_soles <= 4000)).count()),
        ("Más de S/. 4,000", query.filter(Index.m_soles > 4000).count())
    ]

    # Filtrar los rangos con conteo 0
    price_ranges = [(range, count) for range, count in price_ranges if count > 0]

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
        'inicio': formatear_fecha_en_espanol(prod.inicio),
        'precio': f"{prod.m_soles:,.0f}" if prod.m_soles is not None else "",
        'm_soles': str(prod.m_soles),  # Convertir decimales
        'dominio': prod.dominio,
        'tipo': prod.tipo,
        'url_especf': prod.url_especf
    } for prod in productos]

def calculate_filter_options_from_list(productos):
    """
    Calcula las opciones de filtro y sus conteos a partir de una lista de productos.
    :param productos: Lista de productos filtrados.
    :return: dominios, tipos, orgs, price_ranges
    """
    from collections import Counter

    # Contar dominios
    dominios_counter = Counter(prod.dominio for prod in productos if prod.dominio)
    dominios = [(dom, count) for dom, count in dominios_counter.items()]

    # Contar tipos
    tipos_counter = Counter(prod.tipo for prod in productos if prod.tipo)
    tipos = [(tipo, count) for tipo, count in tipos_counter.items()]

    # Contar organizaciones
    orgs_counter = Counter(prod.org for prod in productos if prod.org)
    orgs = [(org, count) for org, count in orgs_counter.items()]

    # Contar rangos de precio
    price_ranges = [
        ("Menos de S/. 500", sum(1 for prod in productos if prod.m_soles and prod.m_soles < 500)),
        ("S/. 500 a S/. 1,000", sum(1 for prod in productos if prod.m_soles and 500 <= prod.m_soles <= 1000)),
        ("S/. 1,000 a S/. 1,500", sum(1 for prod in productos if prod.m_soles and 1000 <= prod.m_soles <= 1500)),
        ("S/. 1,500 a S/. 2,500", sum(1 for prod in productos if prod.m_soles and 1500 <= prod.m_soles <= 2500)),
        ("S/. 2,500 a S/. 4,000", sum(1 for prod in productos if prod.m_soles and 2500 <= prod.m_soles <= 4000)),
        ("Más de S/. 4,000", sum(1 for prod in productos if prod.m_soles and prod.m_soles > 4000)),
    ]

    # Filtrar los rangos con conteo 0
    price_ranges = [(range, count) for range, count in price_ranges if count > 0]

    return dominios, tipos, orgs, price_ranges

