import uuid
from flask_security import hash_password


def initialize_database(app):
    from extensions import db

    with app.app_context():
        db.drop_all()
        db.create_all()

        datastore = app.datastore

        # Create roles
        admin_role   = datastore.find_or_create_role(name='admin',   description='Institute Administrator')
        company_role = datastore.find_or_create_role(name='company', description='Recruiting Company')
        student_role = datastore.find_or_create_role(name='student', description='Placement Student')

        try:
            db.session.commit()
            print("Roles created successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating roles: {e}")

        # Create pre-existing admin (no registration allowed)
        if not datastore.find_user(email='admin@ppa.com'):
            admin_user = datastore.create_user(
                name='Admin',
                email='admin@ppa.com',
                password=hash_password('admin123'),
                fs_uniquifier=str(uuid.uuid4()),
            )
            datastore.add_role_to_user(admin_user, admin_role)

        try:
            db.session.commit()
            print("Admin user created: admin@ppa.com / admin123")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin: {e}")
