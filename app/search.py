from .models import Index
from sqlalchemy import or_
import unicodedata
from .database import db

def normalizar_texto(texto):
    """
    Elimina las tildes y normaliza el texto.
    """
    if texto is None:
        return None
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
        if unicodedata.category(c) != 'Mn'
    )

def realizar_busqueda(query, search_term):
    """
    Realiza una búsqueda insensible a acentos y mayúsculas/minúsculas en la tabla Index basada en un término de búsqueda.
    """
    if search_term:
        # Normalizar el término de búsqueda (sin tildes y en minúsculas)
        search_term_normalizado = normalizar_texto(search_term).lower()

        # Si query es una consulta SQLAlchemy
        if not isinstance(query, list):
            # Obtener todos los resultados de la base de datos para aplicar el filtro manualmente
            resultados = [
                producto for producto in query.all()
                if search_term_normalizado in normalizar_texto(producto.producto or "").lower()
                or search_term_normalizado in normalizar_texto(producto.org or "").lower()
                or search_term_normalizado in normalizar_texto(producto.tipo or "").lower()
            ]
            return resultados

        # Si query ya es una lista, filtrar manualmente
        resultados = [
            producto for producto in query
            if search_term_normalizado in normalizar_texto(producto.producto or "").lower()
            or search_term_normalizado in normalizar_texto(producto.org or "").lower()
            or search_term_normalizado in normalizar_texto(producto.tipo or "").lower()
        ]

        return resultados

    return query.all() if not isinstance(query, list) else query



