import re
from datetime import datetime
from .database import db
from .models import Index

def extract_fecha_dinamica():
    # Obtiene el nombre de la tabla directamente desde la clase Index
    tablename = Index.__tablename__
    
    # Utilizamos expresiones regulares para encontrar los componentes de la fecha en el nombre de la tabla
    match = re.search(r'(\d{2})(\d{2})(\d{2})', tablename)
    if match:
        dia, mes, año = match.groups()
        fecha = f"{int(dia)} de {datetime.strptime(mes, '%m').strftime('%B').lower()} de 20{año}"
        return fecha
    return "Fecha no disponible"

# Esta función ahora no necesita argumentos y puede ser llamada directamente en cualquier lugar donde se necesite la fecha dinámica.
