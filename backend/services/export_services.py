import os
from celery.result import AsyncResult
from flask import current_app, send_file
from tasks import export_as_csv


class ExportService:

    @staticmethod
    def trigger_export(user_id):
        task = export_as_csv.delay(user_id)
        return {
            'message': 'CSV export started.',
            'task_id': task.id,
            'status':  'queued',
        }, 202

    @staticmethod
    def get_export_status(user_id, task_id):
        if not task_id:
            return {'error': 'Task ID is required.'}, 400

        celery_app = current_app.extensions.get('celery')
        if not celery_app:
            return {'error': 'Celery not configured.'}, 500

        result = AsyncResult(task_id, app=celery_app)
        state = result.state

        response = {
            'task_id': task_id,
            'status': state,
            'download_ready': False,
            'download_url': None,
        }

        if state == 'SUCCESS':
            filename = result.result
            if isinstance(filename, str) and filename.startswith(f'student_{user_id}_'):
                response['download_ready'] = True
                response['download_url'] = f'/api/students/{user_id}/export-csv/{task_id}/download'
            else:
                response['status'] = 'FAILURE'
                response['error'] = 'Export did not produce a downloadable file.'

        if state == 'FAILURE':
            response['error'] = str(result.result or 'Export failed.')

        return {'data': response}, 200

    @staticmethod
    def download_export(user_id, task_id):
        celery_app = current_app.extensions.get('celery')
        if not celery_app:
            return {'error': 'Celery not configured.'}, 500

        result = AsyncResult(task_id, app=celery_app)
        if result.state != 'SUCCESS':
            return {'error': 'Export not ready yet.'}, 400

        filename = result.result
        if not isinstance(filename, str) or not filename.startswith(f'student_{user_id}_'):
            return {'error': 'Not authorized to download this file.'}, 403

        file_path = os.path.join('instance', 'exports', filename)
        if not os.path.exists(file_path):
            return {'error': 'Export file not found.'}, 404

        return send_file(file_path, as_attachment=True,
                         download_name=filename, mimetype='text/csv')
