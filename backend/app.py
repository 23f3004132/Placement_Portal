from flask import Flask
from config import LocalDevelopmentConfig

def create_app():
    app = Flask(__name__)
    app.config.from_object(LocalDevelopmentConfig)

    from models import db, User, Role

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app

app = create_app()

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)