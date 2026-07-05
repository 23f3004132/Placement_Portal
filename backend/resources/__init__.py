from flask import Blueprint
from flask_restful import Api

from .auth_resources import LoginResource, RegisterStudentResource, RegisterCompanyResource

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')
api    = Api(api_bp)

# Auth
api.add_resource(LoginResource,           '/login')
api.add_resource(RegisterStudentResource, '/register/student')
api.add_resource(RegisterCompanyResource, '/register/company')