# 🎓 Placement Portal Application (PPA)

A fully functional, production-ready campus placement management system.

**Architecture:** Mirrors the HMS reference repository — Flask-RESTful backend + Vue 3 + Vuex frontend.

---

## 📁 Project Structure

```
PPA_v2/
└── code/
    ├── backend/
    │   ├── app.py                   
    │   ├── config.py                 
    │   ├── extensions.py             
    │   ├── models.py                 
    │   ├── mail.py                   
    │   ├── tasks.py                  
    │   ├── celery_config.py          
    │   ├── requirements.txt
    │   ├── .env                      
    │   ├── resources/                
    │   │   ├── __init__.py           
    │   │   ├── auth_resources.py
    │   │   ├── student_resources.py
    │   │   ├── company_resources.py
    │   │   ├── drive_resources.py
    │   │   ├── application_resources.py
    │   │   └── search_resources.py
    │   ├── services/                 
    │   │   ├── __init__.py
    │   │   ├── auth_services.py
    │   │   ├── student_services.py
    │   │   ├── company_services.py
    │   │   ├── drive_services.py
    │   │   ├── application_services.py
    │   │   ├── search_services.py
    │   │   └── export_services.py
    │   └── scripts/                  
    │       ├── __init__.py
    │       ├── init_db.py            
    │       └── celery_init.py        
    └── frontend/
        ├── index.html
        ├── package.json
        ├── vite.config.js
        └── src/
            ├── main.js
            ├── App.vue
            ├── assets/
            │   └── styles.css        
            ├── utils/
            │   └── api.js            
            ├── store/
            │   └── userStore.js      
            ├── router/
            │   └── index.js          
            └── pages/
                ├── HomePage.vue
                ├── LoginPage.vue
                ├── RegisterPage.vue
                ├── admin/
                │   ├── AdminDashboard.vue   
                │   ├── AdminHome.vue        
                │   ├── AdminCompanies.vue   
                │   ├── AdminStudents.vue    
                │   └── AdminDrives.vue      
                ├── company/
                │   ├── CompanyDashboard.vue
                │   ├── CompanyHome.vue      
                │   ├── CompanyDrives.vue    
                │   ├── CompanyApplications.vue  
                │   └── CompanyProfile.vue   
                └── student/
                    ├── StudentDashboard.vue
                    ├── StudentHome.vue      
                    ├── StudentDrives.vue    
                    ├── StudentApplications.vue  
                    └── StudentProfile.vue   
```

---

## ⚙️ Backend Setup

### Prerequisites
- Python 3.10+
- Redis (for caching + Celery)

### 1. Install dependencies

```bash
cd code/backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Run Flask server

```bash
cd code/backend
python app.py
```

- API: `http://localhost:5000`
- Database auto-created at first run: `instance/database.sqlite3`
- Admin seeded automatically: `admin@ppa.com` / `admin123`

### 4. Run Celery worker (for async jobs)

```bash
cd code/backend
celery -A app.celery worker --loglevel=info
```

### 5. Run Celery Beat (for scheduled jobs)

```bash
cd code/backend
celery -A app.celery beat --loglevel=info
```

---

## 🖥️ Frontend Setup

### Prerequisites
- Node.js 20+

### 1. Install dependencies

```bash
cd code/frontend
npm install
```

### 2. Run development server

```bash
npm run dev
```

Frontend: `http://localhost:5173`

### 3. Build for production

```bash
npm run build
```

---

## 🔐 Default Credentials

| Role    | Email              | Password   |
|---------|--------------------|------------|
| Admin   | admin@ppa.com      | admin123   |

---

## 🔌 API Endpoints

### Auth
| Method | Endpoint                  | Description            |
|--------|---------------------------|------------------------|
| POST   | `/api/login`              | Login (all roles)      |
| POST   | `/api/register/student`   | Register student       |
| POST   | `/api/register/company`   | Register company       |

### Students
| Method | Endpoint                                          | Access         |
|--------|---------------------------------------------------|----------------|
| GET    | `/api/students`                                   | Admin          |
| GET    | `/api/students/<id>`                              | Admin/Student  |
| PATCH  | `/api/students/<id>`                              | Admin/Student  |
| DELETE | `/api/students/<id>`                              | Admin          |
| POST   | `/api/students/<id>/resume`                       | Student        |
| GET    | `/api/students/<id>/resume`                       | All auth       |
| POST   | `/api/students/<id>/export-csv`                   | Student        |
| GET    | `/api/students/<id>/export-csv/<task_id>`         | Student        |
| GET    | `/api/students/<id>/export-csv/<task_id>/download`| Student        |
| GET    | `/api/students/search?name=&branch=&id=`          | Admin          |

### Companies
| Method | Endpoint                           | Access         |
|--------|------------------------------------|----------------|
| GET    | `/api/companies`                   | Admin/Student  |
| GET    | `/api/companies/<id>`              | All auth       |
| PATCH  | `/api/companies/<id>`              | Admin/Company  |
| DELETE | `/api/companies/<id>`              | Admin          |
| GET    | `/api/companies/search?name=`      | Admin/Student  |

### Drives
| Method | Endpoint                      | Access         |
|--------|-------------------------------|----------------|
| GET    | `/api/drives`                 | All auth       |
| POST   | `/api/drives`                 | Company        |
| GET    | `/api/drives/<id>`            | All auth       |
| PATCH  | `/api/drives/<id>`            | Admin/Company  |
| DELETE | `/api/drives/<id>`            | Admin          |
| GET    | `/api/drives/search?name=`    | Admin/Student  |

### Applications
| Method | Endpoint                  | Access         |
|--------|---------------------------|----------------|
| GET    | `/api/applications`       | All auth       |
| POST   | `/api/applications`       | Student        |
| GET    | `/api/applications/<id>`  | All auth       |
| PATCH  | `/api/applications/<id>`  | Admin/Company  |
| DELETE | `/api/applications/<id>`  | Admin/Student  |

---

## 🔄 User Roles & Workflow

```
Admin approves Company → Company creates Drive → Admin approves Drive
                                                         ↓
Student registers → Browses approved drives → Applies → Company reviews
                                                         ↓
                                              Shortlist / Select / Reject
```

---

## ✅ Features Implemented

| Feature                              | Status |
|--------------------------------------|--------|
| Role-based auth (Admin/Company/Student) | ✅ |
| Student registration with all DB fields | ✅ |
| Company registration (3-field form)  | ✅ |
| Admin pre-seeded (no registration)   | ✅ |
| Company approval workflow            | ✅ |
| Drive approval workflow              | ✅ |
| Blacklist companies/students         | ✅ |
| Eligibility validation on apply      | ✅ |
| Duplicate application prevention     | ✅ |
| Resume upload (PDF, base64, ≤5MB)    | ✅ |
| Resume viewer + download             | ✅ |
| Application status tracking          | ✅ |
| Interview type + remarks             | ✅ |
| Search (students, companies, drives) | ✅ |
| CSV export (async Celery job)        | ✅ |
| Daily deadline reminders (Celery)    | ✅ |
| Monthly admin report (Celery Beat)   | ✅ |
| Redis caching                        | ✅ |
| Responsive Bootstrap UI              | ✅ |

---

## 🛠️ Tech Stack

| Layer     | Technology                     |
|-----------|-------------------------------|
| Backend   | Flask 3 + Flask-RESTful        |
| Auth      | Flask-Security-Too (token)     |
| Database  | SQLite + SQLAlchemy 2          |
| Caching   | Redis + Flask-Caching          |
| Jobs      | Celery + Redis                 |
| Frontend  | Vue 3 + Vite                   |
| State     | Vuex 4                         |
| Routing   | Vue Router 4                   |
| HTTP      | Fetch API (no axios)           |
| Styling   | Bootstrap 5 + custom CSS       |
