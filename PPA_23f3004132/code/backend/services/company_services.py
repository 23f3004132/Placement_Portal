from models import db, Company, User


class CompanyService:
    @staticmethod
    def get_all_companies():
        companies = Company.query.all()
        return {'data': [CompanyService._serialize(c) for c in companies]}, 200

    @staticmethod
    def get_company_by_id(user_id):
        c = Company.query.get(user_id)
        if not c:
            return {'error': 'Company not found.'}, 404
        return {'data': CompanyService._serialize(c)}, 200

    @staticmethod
    def update_company(user_id, data):
        c    = Company.query.get(user_id)
        user = User.query.get(user_id)
        if not c:
            return {'error': 'Company not found.'}, 404
        try:
            co_fields = ['company_name', 'hr_contact', 'hr_email', 'website', 'description', 'industry', 'location', 'approval_status']
            for key, value in data.items():
                if value is None:
                    continue
                if key in co_fields:
                    setattr(c, key, value)
                elif key == 'active' and user:
                    user.active = value
                    if not value:
                        for d in c.drives:
                            if d.status == 'approved':
                                d.status = 'closed'
                elif key == 'name' and user:
                    user.name = value

            if data.get('approval_status') == 'blacklisted':
                for d in c.drives:
                    if d.status == 'approved':
                        d.status = 'closed'

            db.session.commit()
            return {'message': 'Company updated.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def delete_company(user_id):
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Company not found.'}, 404
        try:
            db.session.delete(user)
            db.session.commit()
            return {'message': 'Company deleted.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def _serialize(c):
        return {
            'user_id': c.user_id,
            'name': c.user.name,
            'email': c.user.email,
            'active': c.user.active,
            'company_name': c.company_name,
            'hr_contact': c.hr_contact or '',
            'hr_email': c.hr_email or '',
            'website': c.website or '',
            'description': c.description or '',
            'industry': c.industry or '',
            'location': c.location or '',
            'approval_status': c.approval_status,
            'drive_count': len(c.drives),
        }
