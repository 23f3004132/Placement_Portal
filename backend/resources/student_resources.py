import base64
from flask import request
from flask_restful import Resource
from flask_security import auth_required, roles_required, roles_accepted, current_user
from services import StudentService


class StudentListResource(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self):
        return StudentService.get_all_students()


class StudentResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'student', 'company')
    def get(self, user_id):
        if current_user.role == 'student' and current_user.id != user_id:
            return {'error': 'Not authorized.'}, 403
        return StudentService.get_student_by_id(user_id)

    @auth_required('token')
    @roles_accepted('admin', 'student')
    def patch(self, user_id):
        if current_user.role == 'student' and current_user.id != user_id:
            return {'error': 'Not authorized.'}, 403
        data = request.get_json(silent=True) or {}
        return StudentService.update_student(user_id, data)

    @auth_required('token')
    @roles_required('admin')
    def delete(self, user_id):
        return StudentService.delete_student(user_id)


class StudentResumeResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'student', 'company')
    def get(self, user_id):
        if current_user.role == 'student' and current_user.id != user_id:
            return {'error': 'Not authorized.'}, 403
        return StudentService.get_resume(user_id)

    @auth_required('token')
    @roles_accepted('admin', 'student')
    def post(self, user_id):
        if current_user.role == 'student' and current_user.id != user_id:
            return {'error': 'Not authorized.'}, 403
        if 'resume' not in request.files:
            return {'error': "No file. Use field name 'resume'."}, 400
        file = request.files['resume']
        if not file.filename.lower().endswith('.pdf'):
            return {'error': 'Only PDF files allowed.'}, 400
        if len(file.read()) > 5 * 1024 * 1024:
            return {'error': 'File too large. Max 5 MB.'}, 400
        file.seek(0)
        b64 = 'data:application/pdf;base64,' + base64.b64encode(file.read()).decode('utf-8')
        return StudentService.save_resume(user_id, b64)
