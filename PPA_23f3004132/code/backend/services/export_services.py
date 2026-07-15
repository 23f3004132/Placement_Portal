import os
from celery.result import AsyncResult
from flask import current_app, send_file
from tasks import export_as_csv, export_company_applications_as_csv


class ExportService:

    @staticmethod
    def _role_prefix(role):
        return 'company' if role == 'company' else 'student'

    @staticmethod
    def trigger_export(user_id, role='student'):
        task = (
            export_company_applications_as_csv.delay(user_id)
            if role == 'company'
            else export_as_csv.delay(user_id)
        )
        return {
            'message': 'CSV export started.',
            'task_id': task.id,
            'status': 'queued',
        }, 202

    @staticmethod
    def get_export_status(user_id, task_id, role='student'):
        if not task_id:
            return {'error': 'Task ID is required.'}, 400

        celery_app = current_app.extensions.get('celery')
        if not celery_app:
            return {'error': 'Celery not configured.'}, 500

        result = AsyncResult(task_id, app=celery_app)
        state = result.state
        prefix = ExportService._role_prefix(role)

        response = {
            'task_id': task_id,
            'status': state,
            'download_ready': False,
            'download_url': None,
        }

        if state == 'SUCCESS':
            filename = result.result
            if isinstance(filename, str) and filename.startswith(f'{prefix}_{user_id}_'):
                response['download_ready'] = True
                response['download_url'] = f'/api/{prefix}s/{user_id}/export-csv/{task_id}/download'
            else:
                response['status'] = 'FAILURE'
                response['error'] = 'Export did not produce a downloadable file.'

        if state == 'FAILURE':
            response['error'] = str(result.result or 'Export failed.')

        return {'data': response}, 200

    @staticmethod
    def download_export(user_id, task_id, role='student'):
        celery_app = current_app.extensions.get('celery')
        if not celery_app:
            return {'error': 'Celery not configured.'}, 500

        result = AsyncResult(task_id, app=celery_app)
        if result.state != 'SUCCESS':
            return {'error': 'Export not ready yet.'}, 400

        filename = result.result
        prefix = ExportService._role_prefix(role)
        if not isinstance(filename, str) or not filename.startswith(f'{prefix}_{user_id}_'):
            return {'error': 'Not authorized to download this file.'}, 403

        file_path = os.path.join('instance', 'exports', filename)
        if not os.path.exists(file_path):
            return {'error': 'Export file not found.'}, 404

        return send_file(file_path, as_attachment=True,
                         download_name=filename, mimetype='text/csv')
