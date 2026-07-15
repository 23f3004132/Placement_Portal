import csv
import os
from datetime import date, datetime, timedelta
from collections import defaultdict

from celery import shared_task
from jinja2 import Template

from mail import send_email
from models import Application, PlacementDrive, Student, Company, User, now_ist, IST


@shared_task(ignore_result=False, name="export_as_csv")
def export_as_csv(user_id):
    """Export a student's application history as CSV."""
    student = Student.query.filter_by(user_id=user_id).first()
    student_name = student.user.name if student and student.user else User.query.get(user_id).name if User.query.get(user_id) else ''

    applications = (
        Application.query
        .filter_by(student_id=user_id)
        .order_by(Application.application_date.asc())
        .all()
    )

    export_dir = os.path.join('instance', 'exports')
    os.makedirs(export_dir, exist_ok=True)

    filename = f"student_{user_id}_applications_{now_ist().strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join(export_dir, filename)

    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Student ID', 'Student Name', 'Company Name',
            'Drive Title', 'Job Title', 'Application Date',
            'Status', 'Interview Type', 'Remarks',
        ])
        for app in applications:
            writer.writerow([
                user_id,
                student_name,
                app.drive.company.company_name if app.drive and app.drive.company else '',
                app.drive.drive_name if app.drive else '',
                app.drive.job_title if app.drive else '',
                app.application_date,
                app.status,
                app.interview_type or '',
                app.remarks or '',
            ])

    return filename


@shared_task(ignore_result=False, name="export_company_applications_as_csv")
def export_company_applications_as_csv(company_id):
    """Export a company's application history as CSV."""
    company = Company.query.filter_by(user_id=company_id).first()
    if not company:
        return None

    applications = (
        Application.query
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .filter(PlacementDrive.company_id == company_id)
        .order_by(Application.application_date.asc())
        .all()
    )

    export_dir = os.path.join('instance', 'exports')
    os.makedirs(export_dir, exist_ok=True)

    filename = f"company_{company_id}_applications_{now_ist().strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join(export_dir, filename)

    with open(file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Company ID', 'Company Name', 'Student ID', 'Student Name',
            'Branch', 'CGPA', 'Drive Title', 'Job Title',
            'Application Date', 'Status', 'Interview Type', 'Remarks',
        ])
        for app in applications:
            writer.writerow([
                company_id,
                company.company_name,
                app.student_id,
                app.student.user.name if app.student and app.student.user else '',
                app.student.branch if app.student else '',
                app.student.cgpa if app.student else '',
                app.drive.drive_name if app.drive else '',
                app.drive.job_title if app.drive else '',
                app.application_date,
                app.status,
                app.interview_type or '',
                app.remarks or '',
            ])

    return filename


@shared_task(ignore_result=False, name="monthly_activity_report")
def monthly_activity_report():
    """Generate and email monthly placement report to admin."""
    first_day = now_ist().date().replace(day=1)
    last_day_prev  = first_day - timedelta(days=1)
    first_day_prev = last_day_prev.replace(day=1)
    month_label    = first_day_prev.strftime('%B %Y')

    drives = PlacementDrive.query.filter(
        PlacementDrive.created_at >= datetime(first_day_prev.year, first_day_prev.month, 1, tzinfo=IST),
        PlacementDrive.created_at <= datetime(last_day_prev.year, last_day_prev.month, last_day_prev.day, 23, 59, 59, tzinfo=IST),
    ).all()

    total_drives   = len(drives)
    total_applied  = sum(len(d.applications) for d in drives)
    total_selected = sum(
        sum(1 for a in d.applications if a.status == 'selected')
        for d in drives
    )

    drive_rows = ''.join(
        f'<tr><td>{d.drive_name}</td><td>{d.company.company_name if d.company else "-"}</td>'
        f'<td>{len(d.applications)}</td>'
        f'<td>{sum(1 for a in d.applications if a.status == "selected")}</td>'
        f'<td>{d.status}</td></tr>'
        for d in drives
    ) or '<tr><td colspan="5">No drives this month.</td></tr>'

    template = """
    <h2>Monthly Placement Activity Report – {{ month_label }}</h2>
    <p><strong>Total Drives:</strong> {{ total_drives }}</p>
    <p><strong>Total Applications:</strong> {{ total_applied }}</p>
    <p><strong>Total Selected:</strong> {{ total_selected }}</p>
    <br>
    <table border="1" cellpadding="6" cellspacing="0">
      <tr><th>Drive</th><th>Company</th><th>Applications</th><th>Selected</th><th>Status</th></tr>
      {{ drive_rows | safe }}
    </table>
    <p>Regards,<br>Placement Portal System</p>
    """

    message = Template(template).render(
        month_label=month_label,
        total_drives=total_drives,
        total_applied=total_applied,
        total_selected=total_selected,
        drive_rows=drive_rows,
    )

    from models import User
    admins = [u for u in User.query.all() if u.role == 'admin']
    for admin in admins:
        send_email(admin.email, f"Monthly Placement Report – {month_label}", message)

    return f"Monthly report sent for {month_label}"


@shared_task(ignore_result=False, name="daily_reminders")
def daily_reminders():
    """Send deadline reminder emails to students for drives closing today/tomorrow."""
    try:
        today    = now_ist().date()
        tomorrow = today + timedelta(days=1)

        upcoming = PlacementDrive.query.filter(
            PlacementDrive.application_deadline.in_([today, tomorrow]),
            PlacementDrive.status == 'approved'
        ).all()

        if not upcoming:
            return "No upcoming deadlines"

        students = Student.query.join(User).filter(User.active == True).all()

        drive_ids = [d.id for d in upcoming]
        apps = Application.query.filter(Application.drive_id.in_(drive_ids)).all() if drive_ids else []
        applied_map = {}
        for a in apps:
            applied_map.setdefault(a.drive_id, set()).add(a.student_id)

        for student in students:
            remind_drives = [d for d in upcoming if student.user_id not in applied_map.get(d.id, set())]
            if not remind_drives:
                continue

            rows = ''.join(
                f'<tr><td>{d.drive_name}</td>'
                f'<td>{d.company.company_name if d.company else "-"}</td>'
                f'<td>{d.job_title}</td>'
                f'<td>{d.application_deadline}</td></tr>'
                for d in remind_drives
            )

            template = """
            <h3>Dear {{ name }},</h3>
            <p>The following placement drives have approaching deadlines. Apply before it's too late!</p>
            <table border="1" cellpadding="6" cellspacing="0">
              <tr><th>Drive</th><th>Company</th><th>Role</th><th>Deadline</th></tr>
              {{ rows | safe }}
            </table>
            <p>Visit the Placement Portal to apply now.</p>
            <p>Regards,<br>Placement Cell</p>
            """

            message = Template(template).render(name=student.user.name, rows=rows)
            send_email(student.user.email, "Placement Drive Deadline Reminder", message)

        return "Daily reminders sent"
    except Exception as e:
        return f"Error: {str(e)}"
