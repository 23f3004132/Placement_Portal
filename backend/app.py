from flask import Flask
from flask_cors import CORS

from scripts import celery_init_app
from config import LocalDevelopmentConfig

ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]


def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    from models import db, User, Role
    db.init_app(app)
    CORS(app, origins=ALLOWED_ORIGINS)

    from extensions import security, cache
    from flask_security.datastore import SQLAlchemyUserDatastore

    datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, datastore=datastore)
    cache.init_app(app)

    app.datastore = datastore

    from resources import api_bp
    app.register_blueprint(api_bp)

    from scripts import initialize_database
    initialize_database(app)

    return app


app    = create_app()
celery = celery_init_app(app)
celery.autodiscover_tasks()

if __name__ == '__main__':
    app.run(debug=True)
