from datetime import date 
from models import db, PlacementDrive, Company
from flask_security import current_user
from extensions import cache
from flask import current_app as app

def _parse_date(value):  
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip())
    except (ValueError, TypeError):
        return None

class DriveService:
    @staticmethod
    def get_all_drives():
        try:
            role = current_user.role
            # Cache drives list per role (and per company for company role)
            cache_key = f"drives:{role}:{current_user.id if role == 'company' else 'all'}"
            cached = cache.get(cache_key)
            if cached is not None:
                return {'data': cached}, 200

            if role == 'company':
                drives = PlacementDrive.query.filter_by(company_id=current_user.id).all()
            elif role == 'student':
                drives = PlacementDrive.query.filter_by(status='approved').all()
            else:
                drives = PlacementDrive.query.all()

            data = [DriveService._serialize(d) for d in drives]
            cache.set(cache_key, data, timeout=app.config.get('CACHE_DEFAULT_TIMEOUT', 300))
            return {'data': data}, 200
        except Exception as e:
            return {'error': str(e)}, 500

    @staticmethod
    def get_drive_by_id(drive_id):
        d = PlacementDrive.query.get(drive_id)
        if not d:
            return {'error': 'Drive not found.'}, 404
        return {'data': DriveService._serialize(d)}, 200

    @staticmethod
    def create_drive(data):
        company_id = data.get('company_id') or current_user.id
        company    = Company.query.get(company_id)
        if not company or company.approval_status != 'approved':
            return {'error': 'Company must be approved before creating drives.'}, 403
        try:
            drive = PlacementDrive(
                company_id = company_id,
                drive_name = data.get('drive_name', ''),
                job_title = data.get('job_title', ''),
                job_description = data.get('job_description', ''),
                eligibility_branch = data.get('eligibility_branch', ''),
                eligibility_cgpa = float(data.get('eligibility_cgpa') or 0.0),
                eligibility_year = int(data.get('eligibility_year') or 0) or None,
                salary = data.get('salary', ''),
                location = data.get('location', ''),
                application_deadline = _parse_date(data.get('application_deadline')),  # ← CHANGE THIS
                status = 'pending',
            )
            db.session.add(drive)
            db.session.commit()
        
            try:
                cache.clear()
            except Exception:
                pass
            return {'message': 'Drive created. Pending admin approval.'}, 201
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def update_drive(drive_id, data):
        d = PlacementDrive.query.get(drive_id)
        if not d:
            return {'error': 'Drive not found.'}, 404
        try:
            allowed = ['drive_name', 'job_title', 'job_description', 'eligibility_branch',
                       'eligibility_cgpa', 'eligibility_year', 'salary', 'location',
                       'application_deadline', 'status']
            for key, value in data.items():
                if value is None or key not in allowed:
                    continue
                if key == 'application_deadline':     
                    setattr(d, key, _parse_date(value))
                else:
                    setattr(d, key, value)
            db.session.commit()
            try:
                cache.clear()
            except Exception:
                pass
            return {'message': 'Drive updated.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def delete_drive(drive_id):
        d = PlacementDrive.query.get(drive_id)
        if not d:
            return {'error': 'Drive not found.'}, 404
        try:
            db.session.delete(d)
            db.session.commit()
            try:
                cache.clear()
            except Exception:
                pass
            return {'message': 'Drive deleted.'}, 200
        except Exception as e:
            db.session.rollback()
            return {'error': str(e)}, 500

    @staticmethod
    def _serialize(d):
        return {
            'id': d.id,
            'company_id': d.company_id,
            'company_name': d.company.company_name if d.company else 'N/A',
            'company_location': d.company.location     if d.company else '',
            'drive_name': d.drive_name,
            'job_title': d.job_title,
            'job_description': d.job_description or '',
            'eligibility_branch': d.eligibility_branch or '',
            'eligibility_cgpa': d.eligibility_cgpa or 0.0,
            'eligibility_year': d.eligibility_year,
            'salary': d.salary or '',
            'location': d.location or '',
            'application_deadline': str(d.application_deadline) if d.application_deadline else None,
            'status': d.status,
            'created_at': str(d.created_at),
            'applicant_count': len(d.applications),
        }