from flask import request
from flask_restful import Resource
from flask_security import auth_required, roles_required, roles_accepted, current_user
from services import CompanyService


class CompanyListResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'student')
    def get(self):
        return CompanyService.get_all_companies()

class CompanyResource(Resource):
    @auth_required('token')
    @roles_accepted('admin', 'company', 'student')
    def get(self, user_id):
        return CompanyService.get_company_by_id(user_id)

    @auth_required('token')
    @roles_accepted('admin', 'company')
    def patch(self, user_id):
        if current_user.role == 'company' and current_user.id != user_id:
            return {'error': 'Not authorized.'}, 403
        data = request.get_json(silent=True) or {}
        return CompanyService.update_company(user_id, data)

    @auth_required('token')
    @roles_required('admin')
    def delete(self, user_id):
        return CompanyService.delete_company(user_id)
