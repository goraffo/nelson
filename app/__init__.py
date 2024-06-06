from flask import Flask
from .database import db
import os

def create_app():
    app = Flask(__name__)
    # Usa la variable de entorno DATABASE_URL para la conexión a la base de datos
    database_url = os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:malacca87@localhost/edec_index')
    if 'sslmode' not in database_url:
        database_url += '?sslmode=require&sslrootcert=/path/to/root.crt&sslcert=/path/to/postgresql.crt&sslkey=/path/to/postgresql.key'
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # with app.app_context():
    #     db.create_all()

    from .views import init_views
    init_views(app)

    return app
