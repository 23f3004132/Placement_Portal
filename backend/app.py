from flask import Flask
from config import LocalDevelopmentConfig
from dotenv import load_dotenv


def create_app():
    app = Flask(__name__)

    load_dotenv() 
    
    app.config.from_object(LocalDevelopmentConfig)

    from models import db, User, Role
    db.init_app(app)

    from extensions import security
    from flask_security.datastore import SQLAlchemyUserDatastore

    datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app, datastore=datastore)

    app.datastore = datastore

    from scripts.init_db import initialize_database

    initialize_database(app)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)