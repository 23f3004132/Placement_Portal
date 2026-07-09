from flask_restful import Resource, reqparse
from flask_security import auth_required, roles_required, roles_accepted
from services import SearchService

search_parser = reqparse.RequestParser()
search_parser.add_argument('name', type=str, location='args')
search_parser.add_argument('branch', type=str, location='args')
search_parser.add_argument('industry', type=str, location='args')
search_parser.add_argument('company', type=str, location='args')
search_parser.add_argument('id', type=int, location='args')


class SearchStudentResource(Resource):

    @auth_required('token')
    @roles_required('admin')
    def get(self):
        args = search_parser.parse_args()
        return SearchService.search_students(
            name=args.get('name'),
            branch=args.get('branch'),
            student_id=args.get('id'),
        )


class SearchCompanyResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'student')
    def get(self):
        args = search_parser.parse_args()
        return SearchService.search_companies(
            name=args.get('name'),
            industry=args.get('industry'),
        )


class SearchDriveResource(Resource):

    @auth_required('token')
    @roles_accepted('admin', 'student')
    def get(self):
        args = search_parser.parse_args()
        return SearchService.search_drives(
            name=args.get('name'),
            company=args.get('company'),
        )
