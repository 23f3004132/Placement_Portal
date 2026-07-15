import uuid
from flask import current_app as app
from flask_security import hash_password, verify_password
from models import db, User, Student, Company


class AuthService:
    @staticmethod
    def login(data):
        email = data.get('email', '').strip()
        password = data.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user and verify_password(password, user.password):
            if not user.active:
                return {'error': 'Your account has been blocked. Please contact the placement cell.'}, 403

            if user.role == 'company' and user.company:
                status = user.company.approval_status
                if status == 'pending':
                    return {'error': 'Company registration pending admin approval.'}, 403
                if status in ('rejected', 'blacklisted'):
                    return {'error': f'Company account has been {status}.'}, 403
            return {
                'message': 'Login successful.',
                'user_id': user.id,
                'access_token': user.get_auth_token(),
                'role': user.role,
                'name': user.name,
            }, 200

        return {'error': 'Invalid email or password.'}, 401

    @staticmethod
    def register_student(data):
        email = data.get('email', '').strip()
        name  = data.get('name', '').strip()

        if not email or not data.get('password') or not name:
            return {'error': 'Name, email and password are required.'}, 400

        if User.query.filter_by(email=email).first():
            return {'error': 'Email already registered.'}, 400

        datastore = app.datastore
        try:
            new_user = datastore.create_user(
                name = name,
                email = email,
                password = hash_password(data.get('password')),
                fs_uniquifier = str(uuid.uuid4()),
            )
            datastore.add_role_to_user(new_user, 'student')
            db.session.flush()

            student = Student(
                user_id = new_user.id,
                branch = data.get('branch', ''),
                cgpa = float(data.get('cgpa') or 0.0),
                year = int(data.get('year') or 0) or None,
                contact_number = data.get('contact_number', ''),
                skills = data.get('skills', ''),
                address = data.get('address', ''),
            )
            db.session.add(student)
            db.session.commit()
            return {'message': 'Student registration successful.', 'user_id': new_user.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': f'Registration failed: {e}'}, 500

    @staticmethod
    def register_company(data):
        email = data.get('email', '').strip()
        company_name = data.get('company_name', '').strip()

        if not email or not data.get('password') or not company_name:
            return {'error': 'Company name, email and password are required.'}, 400

        if User.query.filter_by(email=email).first():
            return {'error': 'Email already registered.'}, 400

        datastore = app.datastore
        try:
            new_user = datastore.create_user(
                name = company_name,
                email = email,
                password = hash_password(data.get('password')),
                fs_uniquifier = str(uuid.uuid4()),
            )
            datastore.add_role_to_user(new_user, 'company')
            db.session.flush()

            company = Company(
                user_id = new_user.id,
                company_name = company_name,
                approval_status = 'pending',
            )
            db.session.add(company)
            db.session.commit()
            return {'message': 'Company registered. Awaiting admin approval.', 'user_id': new_user.id}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': f'Registration failed: {e}'}, 500
