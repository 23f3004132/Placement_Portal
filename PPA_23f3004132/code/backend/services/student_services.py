from flask_security import hash_password
from models import db, Student, User

class StudentService:
    @staticmethod
    def get_all_students():
        students = Student.query.all()
        return {'data': [StudentService._serialize(s) for s in students]}, 200

    @staticmethod
    def get_student_by_id(user_id):
        s = Student.query.get(user_id)
        if not s:
            return {'error': 'Student not found.'}, 404
        return {'data': StudentService._serialize(s)}, 200

    @staticmethod
    def update_student(user_id, data):
        s = Student.query.get(user_id)
        user = User.query.get(user_id)
        if not s:
            return {'error': 'Student not found.'}, 404
        try:
            student_fields = ['branch', 'cgpa', 'year', 'contact_number', 'skills', 'address']
            user_fields = ['name', 'email', 'active']
            for key, value in data.items():
                if value is None:
                    continue
                if key == 'password':
                    user.password = hash_password(value)
                elif key in user_fields:
                    setattr(user, key, value)
                elif key in student_fields:
                    setattr(s, key, value)
            db.session.commit()
            return {'message': 'Profile updated successfully.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def delete_student(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Student not found.'}, 404
        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'Student deleted.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def save_resume(user_id, b64_data):
        s = Student.query.get(user_id)
        if not s:
            return {'error': 'Student not found.'}, 404
        try:
            s.resume_data = b64_data
            db.session.commit()
            return {'message': 'Resume uploaded.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def get_resume(user_id):
        s = Student.query.get(user_id)
        if not s:
            return {'error': 'Student not found.'}, 404
        if not s.resume_data:
            return {'error': 'No resume uploaded.'}, 404
        return {'data': {'resume': s.resume_data}}, 200

    @staticmethod
    def _serialize(s):
        return {
            'user_id': s.user_id,
            'name': s.user.name,
            'email': s.user.email,
            'active': s.user.active,
            'branch': s.branch or '',
            'cgpa': s.cgpa or 0.0,
            'year': s.year,
            'contact_number': s.contact_number or '',
            'skills': s.skills or '',
            'address': s.address or '',
            'has_resume': bool(s.resume_data),
        }
