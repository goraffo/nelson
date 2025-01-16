from .database import db

class Index(db.Model):
    __tablename__ = 'index250111'

    id_impresion = db.Column(db.Integer, primary_key=True)
    org = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(100), nullable=False)
    url_madre = db.Column(db.Text, nullable=True)
    eje = db.Column(db.String(255), nullable=False)
    producto = db.Column(db.String(255), nullable=False)
    dominio = db.Column(db.String(100), nullable=False)
    url_especf = db.Column(db.Text, nullable=True)
    precio = db.Column(db.String(255), nullable=True)
    m_soles = db.Column(db.Numeric, nullable=True)
    horas_tot = db.Column(db.Float, nullable=True)  # Cambiado de Integer a Float
    duracion = db.Column(db.String(255), nullable=True)
    lanzamiento = db.Column(db.String(255), nullable=True)
    inicio = db.Column(db.Date, nullable=True)
