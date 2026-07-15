from flask import request
from flask_restful import Resource
from flask_security import auth_required, roles_required, roles_accepted, current_user
from services import DriveService


class DriveListResource(Resource):

    @auth_required('token')
    def get(self):
        return DriveService.get_all_drives()

    @auth_required('token')
    @roles_required('company')
    def post(self):
        data = request.get_json(silent=True) or {}
        return DriveService.create_drive(data)


class DriveResource(Resource):

    @auth_required('token')
    def get(self, drive_id):
        return DriveService.get_drive_by_id(drive_id)

    @auth_required('token')
    @roles_accepted('admin', 'company')
    def patch(self, drive_id):
        data = request.get_json(silent=True) or {}
        return DriveService.update_drive(drive_id, data)

    @auth_required('token')
    @roles_required('admin')
    def delete(self, drive_id):
        return DriveService.delete_drive(drive_id)
