from models import db, Application, PlacementDrive, Student
from flask_security import current_user


class ApplicationService:

    @staticmethod
    def get_all_applications():
        try:
            role = current_user.role
            if role == 'student':
                apps = Application.query.filter_by(student_id=current_user.id).all()
            elif role == 'company':
                drive_ids = [d.id for d in current_user.company.drives]
                apps = Application.query.filter(Application.drive_id.in_(drive_ids)).all()
            else:
                apps = Application.query.all()
            return {'data': [ApplicationService._serialize(a) for a in apps]}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    @staticmethod
    def get_application_by_id(app_id):
        a = Application.query.get(app_id)
        if not a:
            return {'error': 'Application not found.'}, 404
        return {'data': ApplicationService._serialize(a)}, 200

    @staticmethod
    def create_application(data):
        student_id = data.get('student_id') or current_user.id
        drive_id   = data.get('drive_id')

        if Application.query.filter_by(student_id=student_id, drive_id=drive_id).first():
            return {'error': 'Already applied to this drive.'}, 400

        drive = PlacementDrive.query.get(drive_id)
        if not drive or drive.status != 'approved':
            return {'error': 'Drive is not available.'}, 400

        # Eligibility validation
        student = Student.query.get(student_id)
        if student:
            if drive.eligibility_cgpa and (not student.cgpa or student.cgpa < drive.eligibility_cgpa):
                return {'error': f'Minimum CGPA of {drive.eligibility_cgpa} required.'}, 400
            if drive.eligibility_year and student.year and student.year != drive.eligibility_year:
                return {'error': f'Only Year {drive.eligibility_year} students are eligible.'}, 400
            if drive.eligibility_branch and drive.eligibility_branch.strip().lower() not in ('any', ''):
                allowed = [b.strip().lower() for b in drive.eligibility_branch.split(',')]
                if student.branch and student.branch.strip().lower() not in allowed:
                    return {'error': 'Your branch is not eligible for this drive.'}, 400

        try:
            app = Application(student_id=student_id, drive_id=drive_id)
            db.session.add(app)
            db.session.commit()
            return {'message': 'Application submitted successfully.'}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def update_application(app_id, data):
        a = Application.query.get(app_id)
        if not a:
            return {'error': 'Application not found.'}, 404
        try:
            for key in ('status', 'interview_type', 'remarks'):
                if key in data and data[key] is not None:
                    setattr(a, key, data[key])
            db.session.commit()
            return {'message': 'Application updated.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def delete_application(app_id):
        a = Application.query.get(app_id)
        if not a:
            return {'error': 'Application not found.'}, 404
        try:
            db.session.delete(a)
            db.session.commit()
            return {'message': 'Application withdrawn.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def _serialize(a):
        return {
            'id': a.id,
            'student_id': a.student_id,
            'student_name': a.student.user.name if a.student else 'N/A',
            'student_branch': a.student.branch if a.student else '',
            'student_cgpa': a.student.cgpa if a.student else None,
            'has_resume': bool(a.student.resume_data) if a.student else False,
            'drive_id': a.drive_id,
            'drive_name': a.drive.drive_name if a.drive else 'N/A',
            'job_title': a.drive.job_title if a.drive else 'N/A',
            'company_name': a.drive.company.company_name if (a.drive and a.drive.company) else 'N/A',
            'company_id': a.drive.company_id   if a.drive else None,
            'application_date': str(a.application_date),
            'status': a.status,
            'interview_type': a.interview_type or '',
            'remarks': a.remarks or '',
        }
