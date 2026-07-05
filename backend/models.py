from extensions import db
from flask_security import UserMixin, RoleMixin
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    active = db.Column(db.Boolean(), default=True)

    roles = db.relationship('Role', secondary='user_roles', backref='bearers')
    student = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    company = db.relationship('Company', backref='user', uselist=False, cascade='all, delete-orphan')

    @property
    def role(self):
        return self.roles[0].name if self.roles else None


class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))


class UserRoles(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))


class Student(db.Model):
    __tablename__ = 'students'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    branch = db.Column(db.String(100))
    cgpa = db.Column(db.Float, default=0.0)
    year = db.Column(db.Integer)
    contact_number = db.Column(db.String(20))
    skills = db.Column(db.String(500))
    address = db.Column(db.String(300))
    resume_data = db.Column(db.Text)   # base64-encoded PDF

    applications = db.relationship('Application', backref='student', cascade='all, delete-orphan', lazy=True)


class Company(db.Model):
    __tablename__ = 'companies'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    company_name = db.Column(db.String(255), nullable=False)
    hr_contact = db.Column(db.String(100))
    hr_email = db.Column(db.String(255))
    website = db.Column(db.String(255))
    description = db.Column(db.Text)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))
    approval_status = db.Column(db.Enum('pending', 'approved', 'rejected', 'blacklisted', name='co_status'), default='pending', nullable=False)

    drives = db.relationship('PlacementDrive', backref='company', cascade='all, delete-orphan', lazy=True)


class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.user_id'), nullable=False)
    drive_name = db.Column(db.String(255), nullable=False)
    job_title = db.Column(db.String(255), nullable=False)
    job_description = db.Column(db.Text)
    eligibility_branch = db.Column(db.String(255))
    eligibility_cgpa = db.Column(db.Float, default=0.0)
    eligibility_year = db.Column(db.Integer)
    salary = db.Column(db.String(100))
    location = db.Column(db.String(100))
    application_deadline = db.Column(db.Date)
    status = db.Column(db.Enum('pending', 'approved', 'closed', 'rejected', name='drive_status'), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship('Application', backref='drive', cascade='all, delete-orphan', lazy=True)


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.user_id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('applied', 'shortlisted', 'selected', 'rejected', name='app_status'), default='applied', nullable=False)
    interview_type = db.Column(db.String(50))
    remarks = db.Column(db.String(500))

    __table_args__ = (db.UniqueConstraint('student_id', 'drive_id', name='uq_student_drive'),)
