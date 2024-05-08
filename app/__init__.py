from flask import Flask
from .database import db

def create_app():
    app = Flask(__name__)
    # Asegúrate de reemplazar 'tu_contraseña' con la contraseña real del usuario 'postgres'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:43manaties@localhost/edec_index'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    from .views import init_views
    init_views(app)

    return app