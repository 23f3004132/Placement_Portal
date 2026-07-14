from flask import Blueprint
from flask_restful import Api

from .auth_resources import LoginResource, RegisterStudentResource, RegisterCompanyResource
from .student_resources import (StudentListResource, StudentResource, StudentResumeResource)
from .company_resources import CompanyListResource, CompanyResource
from .drive_resources import DriveListResource, DriveResource
from .application_resources import ApplicationListResource, ApplicationResource
from .search_resources import SearchStudentResource, SearchCompanyResource, SearchDriveResource
from .student_resources import StudentExportResource

api_bp = Blueprint('api_bp', __name__, url_prefix='/api')
api    = Api(api_bp)

# Auth
api.add_resource(LoginResource, '/login')
api.add_resource(RegisterStudentResource, '/register/student')
api.add_resource(RegisterCompanyResource, '/register/company')

# Students
api.add_resource(StudentListResource, '/students')
api.add_resource(StudentResource, '/students/<int:user_id>')
api.add_resource(StudentResumeResource, '/students/<int:user_id>/resume')
api.add_resource(SearchStudentResource, '/students/search')

# Companies
api.add_resource(CompanyListResource, '/companies')
api.add_resource(CompanyResource, '/companies/<int:user_id>')
api.add_resource(SearchCompanyResource, '/companies/search')

# Drives
api.add_resource(DriveListResource, '/drives')
api.add_resource(DriveResource, '/drives/<int:drive_id>')
api.add_resource(SearchDriveResource, '/drives/search')

# Applications
api.add_resource(ApplicationListResource, '/applications')
api.add_resource(ApplicationResource, '/applications/<int:app_id>')


# Student export endpoints: trigger, status, download (single registration)
api.add_resource(StudentExportResource,
				 '/students/<int:user_id>/export-csv',
				 '/students/<int:user_id>/export-csv/<string:task_id>',
				 '/students/<int:user_id>/export-csv/<string:task_id>/download')
