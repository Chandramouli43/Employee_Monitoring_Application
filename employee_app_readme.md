# Employee Monitoring App - Full README

## Overview
This document provides a complete end-to-end README for the Employee Monitoring App, including architecture, setup, environment variables, run instructions, and module-level explanations.

---

## 1. System Architecture

### **Architecture Diagram (Enhanced Visual)**
```
                ┌──────────────────────────────┐
                │          FRONTEND            │
                │        (React / Vite)        │
                └──────────────┬───────────────┘
                               │ REST API
                               ▼
 ┌──────────────────────────────────────────────────────────┐
 │                        FASTAPI BACKEND                   │
 │  ┌─────────────────────────────┬───────────────────────┐ │
 │  │  Auth Module                │ Monitoring Module     │ │
 │  ├─────────────────────────────┼───────────────────────┤ │
 │  │  JWT, RBAC                  │ Activity Logging       │ │
 │  │  Sessions                   │ Screenshot API         │ │
 │  │                             │ Productivity Scores    │ │
 │  └─────────────────────────────┴───────────────────────┘ │
 │                │                        │                 │
 └────────────────┼────────────────────────┼─────────────────┘
                  │                        │
                  ▼                        ▼
      ┌───────────────────┐      ┌─────────────────────────┐
      │  PostgreSQL DB    │      │  FILE STORAGE (S3)      │
      │ users, logs, meta │      │ screenshots, exports    │
      └───────────────────┘      └─────────────────────────┘
                  │                        │
                  ▼                        ▼
         ┌────────────────┐       ┌──────────────────────────┐
         │ Worker (Celery │◄──────│   Scheduled Jobs         │
         │ / APScheduler) │       │ screenshot tasks, cleanup│
         └────────────────┘       └──────────────────────────┘
```
The system follows a modular, service-oriented architecture with clear separation of concerns:

### **High-Level Components**
- **Backend (FastAPI)** – Handles authentication, employee activity tracking, reporting, admin functions, and API integrations.
- **Database (PostgreSQL / MySQL)** – Stores users, activity logs, screenshots, events, and reports.
- **Scheduler / Worker (Celery / APScheduler)** – Background jobs for screenshot capturing, cleanup, reporting, alerts.
- **Frontend (React)** – Admin & employee dashboards.
- **File Storage (AWS S3 / Local)** – Stores screenshots or monitoring assets.

### **Architecture Diagram (Text Version)**
```
 ┌──────────────┐        ┌──────────────┐
 │   Frontend   │ <────> │   FastAPI    │ <─────> Database
 └──────────────┘        └──────────────┘
          ▲                    │
          │                    ▼
          │              Background Worker
          │                    │
          ▼                    ▼
     Employee App      Screenshot Storage (S3)
```

---

## 2. Features
- User Authentication (JWT)
- Role-based Access Control (Admin, Manager, Employee)
- Real-time Activity Monitoring
- Periodic Screenshots
- Productivity Analysis Dashboard
- Alerts & Notifications
- Reports (daily, weekly, monthly)
- API integrations (future expansion)

---

## 3. Folder Structure
```
backend/
│── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── utils/
│── tests/
│── .env
│── main.py
frontend/
│── src/
│── public/
│── package.json
infra/
│── docker-compose.yml
│── nginx.conf
```

---

## 4. Backend Setup (FastAPI)

### **1. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Apply Migrations**
```bash
alembic upgrade head
```

### **4. Run the Server**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
You can access the API docs at:
```
http://localhost:8000/docs
```

---

## 5. Environment Variables
Create a `.env` file in the backend root:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/monitoring
JWT_SECRET=your_secret
JWT_ALGORITHM=HS256
AWS_ACCESS_KEY=xxx
AWS_SECRET_KEY=xxx
S3_BUCKET=my-monitoring-bucket
```

---

## 6. Frontend Setup (React)
```bash
cd frontend
npm install
npm run dev
```
## Default Login id
Default admin created: admin@example.com / admin123
---

## 7. Docker Setup (Optional)
### **1. docker-compose.yml Overview**
```
services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - backend/.env
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: admin
      POSTGRES_DB: monitoring
    ports:
      - "5432:5432"
    volumes:
      - db_data:/var/lib/postgresql/data

  nginx:
    build: ./infra/nginx
    ports:
      - "80:80"
    depends_on:
      - api

volumes:
  db_data:
```

### **2. Run**
```bash
docker-compose up --build
```

### **3. What Happens Internally**
- Backend container runs FastAPI with Uvicorn
- DB service initializes PostgreSQL with persistent volume
- Nginx reverse-proxies API requests
- Health checks ensure API is reachable

---

## 8. How Monitoring Works
1. Agent tracks activity events.
2. Worker triggers screenshot jobs.
3. Screenshots uploaded to S3.
4. FastAPI API stores metadata.
5. Admin dashboard retrieves insights.

---

## 9. API Overview
### Authentication
- `POST /auth/login`
- `POST /auth/register`

### Monitoring
- `POST /activities/`
- `POST /screenshots/`
- `GET /reports/{employee_id}`

---

## 10. Deployment Guide
### **Option A: Docker + Cloud VM**
- AWS EC2 / DigitalOcean Droplet
- Docker Compose
- Nginx reverse proxy
- SSL via Certbot

### **Option B: Serverless**
- API on AWS Lambda
- Screenshots on S3
- DB on RDS

---

## 11. Troubleshooting
### **Common Issues (Expanded)**

#### **1. API not starting inside Docker**
**Cause:** Missing environment variables.  
**Fix:** Ensure `.env` exists *inside* backend folder.

#### **2. React app cannot reach API**
**Cause:** Wrong API base URL.
Fix: in `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

#### **3. Screenshots not uploading**
- Check S3 permissions (`PutObject`, `GetObject`)
- Verify worker / scheduler is actually running

#### **4. Migrations failing**
Run:
```bash
alembic revision --autogenerate -m "fix models"
alembic upgrade head
```
- **DB Connection Error** → Check DATABASE_URL
- **CORS Issues** → Update FastAPI CORS middleware
- **Failed Screenshots** → Verify worker is running
- **JWT expired** → Extend expiry settings

---

## 12. Future Enhancements
- AI-based productivity scoring
- Mouse & keyboard heatmaps
- Real-time streaming of screens
- Mobile app

---

## 13. Conclusion
This README provides all essential details to run, deploy, extend, and understand the Employee Monitoring App architecture.

---

## Additional Resources (Generated)
I generated a GitHub-optimized README and several diagrams (SVGs) you can download and include in your repository or docs. Files are saved to the sandbox paths below — use them directly or commit them to your repo.

- `sandbox:/mnt/data/EMPLOYEE_MONITORING_APP_README_GITHUB.md` — GitHub-ready README (badges, TOC, quickstart, onboarding guide).
- `sandbox:/mnt/data/architecture_diagram.svg` — Deployment-ready architecture diagram (SVG).
- `sandbox:/mnt/data/uml_sequence.svg` — UML sequence diagram (SVG).
- `sandbox:/mnt/data/uml_class.svg` — UML class diagram (SVG).
- `sandbox:/mnt/data/erd.svg` — Entity-relationship diagram (SVG).

You can download these from the chat (links provided) or copy them into your repo under an `/docs` or `/assets/diagrams` folder.

---

If you want, I can:
- Export the architecture diagram as PNG as well.
- Create higher-fidelity UML diagrams in PlantUML or draw.io format.
- Inject the GitHub README into your repo and open a PR (if you provide the remote URL).

Tell me which of those you want next and I’ll produce them.

