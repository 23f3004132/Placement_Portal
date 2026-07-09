from flask import request
from flask_restful import Resource
from flask_security import auth_required, roles_required, roles_accepted, current_user
from services import ApplicationService


class ApplicationListResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'company', 'student')
    def get(self):
        return ApplicationService.get_all_applications()

    @auth_required('token')
    @roles_required('student')
    def post(self):
        data = request.get_json(silent=True) or {}
        return ApplicationService.create_application(data)


class ApplicationResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'company', 'student')
    def get(self, app_id):
        return ApplicationService.get_application_by_id(app_id)

    @auth_required('token')
    @roles_accepted('admin', 'company')
    def patch(self, app_id):
        data = request.get_json(silent=True) or {}
        return ApplicationService.update_application(app_id, data)

    @auth_required('token')
    @roles_accepted('admin', 'student')
    def delete(self, app_id):
        return ApplicationService.delete_application(app_id)
