from models import Student, Company, PlacementDrive, User
from extensions import cache
from flask import current_app as app


class SearchService:

    @staticmethod
    def search_students(name=None, branch=None, student_id=None):
        # Cache by query params
        cache_key = f"search_students:{name or ''}:{branch or ''}:{student_id or ''}"
        cached = cache.get(cache_key)
        if cached is not None:
            return {'data': cached}, 200

        query = Student.query.join(User)
        if student_id:
            query = query.filter(Student.user_id == student_id)
        if name:
            query = query.filter(User.name.ilike(f'%{name}%'))
        if branch:
            query = query.filter(Student.branch.ilike(f'%{branch}%'))
        students = query.all()
        data = [{
                'user_id': s.user_id,
                'name': s.user.name,
                'email': s.user.email,
                'branch': s.branch or '',
                'cgpa': s.cgpa or 0.0,
                'year': s.year,
                'active': s.user.active,
                'has_resume': bool(s.resume_data),
            } for s in students]
        cache.set(cache_key, data, timeout=app.config.get('CACHE_DEFAULT_TIMEOUT', 300))
        return {'data': data}, 200

    @staticmethod
    def search_companies(name=None, industry=None):
        cache_key = f"search_companies:{name or ''}:{industry or ''}"
        cached = cache.get(cache_key)
        if cached is not None:
            return {'data': cached}, 200

        query = Company.query.join(User)
        if name:
            query = query.filter(Company.company_name.ilike(f'%{name}%'))
        if industry:
            query = query.filter(Company.industry.ilike(f'%{industry}%'))
        companies = query.all()
        data = [{
                'user_id': c.user_id,
                'company_name': c.company_name,
                'email': c.user.email,
                'industry': c.industry or '',
                'location': c.location or '',
                'approval_status': c.approval_status,
                'drive_count': len(c.drives),
            } for c in companies]
        cache.set(cache_key, data, timeout=app.config.get('CACHE_DEFAULT_TIMEOUT', 300))
        return {'data': data}, 200

    @staticmethod
    def search_drives(name=None, company=None):
        cache_key = f"search_drives:{name or ''}:{company or ''}"
        cached = cache.get(cache_key)
        if cached is not None:
            return {'data': cached}, 200

        query = PlacementDrive.query.filter_by(status='approved')
        if name:
            query = query.filter(PlacementDrive.drive_name.ilike(f'%{name}%'))
        if company:
            query = query.join(Company).filter(Company.company_name.ilike(f'%{company}%'))
        drives = query.all()
        data = [{
                'id': d.id,
                'drive_name': d.drive_name,
                'job_title': d.job_title,
                'company_name': d.company.company_name if d.company else 'N/A',
                'status': d.status,
                'application_deadline': str(d.application_deadline) if d.application_deadline else None,
            } for d in drives]
        cache.set(cache_key, data, timeout=app.config.get('CACHE_DEFAULT_TIMEOUT', 300))
        return {'data': data}, 200
