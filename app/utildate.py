import re
from datetime import datetime
from .database import db
from .models import Index

def extract_fecha_dinamica():
    # Obtiene el nombre de la tabla directamente desde la clase Index
    tablename = Index.__tablename__
    
    # Ajustar la expresión regular para extraer correctamente la fecha
    # El nuevo formato asume que el nombre de la tabla termina en día, mes y luego año (todo en dos dígitos)
    match = re.search(r'index(\d{2})(\d{2})(\d{2})$', tablename)
    if match:
        día, mes, año = match.group(3), match.group(2), match.group(1)  # Reordenar según tu formato
        fecha = f"{int(día)} de {datetime.strptime(mes, '%m').strftime('%B').lower()} de 20{año}"
        return fecha
    return "Fecha no disponible"

# Esta función ahora interpreta correctamente la fecha en el formato especificado.
