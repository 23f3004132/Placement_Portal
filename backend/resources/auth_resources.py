from flask import request
from flask_restful import Resource
from services import AuthService


class LoginResource(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        if not data.get('email') or not data.get('password'):
            return {'error': 'Email and password are required.'}, 400
        return AuthService.login(data)


class RegisterStudentResource(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        return AuthService.register_student(data)


class RegisterCompanyResource(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        return AuthService.register_company(data)
